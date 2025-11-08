"""
Preload Results for AI Showcase App

Generates simulation results for all 15 scenarios (5 press counts × 3 mixes)
with 3 methods each: Baseline (no coordination), Static Cardiac (default params),
and AI-Optimized Cardiac (from AI recommendations).

METHODOLOGY NOTE:
- Uses seed=42 for consistency across all simulations
- Represents a SINGLE deployment scenario (not averaged across seeds)
- This mirrors real-world deployment where you program initial machine states
- Validation testing (docs/DETAILED_VALIDATION_RESULTS.md) uses 5 seeds + averaging
- The showcase demonstrates "what you would see in production with seed=42"

For statistical validation results (5-seed averages), see:
- docs/DETAILED_VALIDATION_RESULTS.md
- results/validation/validation_detailed_by_seed.csv

Usage:
    python src/heart_sim/showcase/preload_results.py

Output:
    src/heart_sim/showcase/data/showcase_results.pkl
    src/heart_sim/showcase/data/showcase_results.json (summary)
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.heart_sim import (
    create_coordinator_auto,
    SimulationEngine,
)
from src.heart_sim.power_profiles import create_press_fleet
from src.heart_sim.press import PressConfig
from src.heart_sim.coordination import CardiacCoordinator
from tests.test_framework import ScenarioConfig


# Static cardiac parameters (Phase 5 baseline)
STATIC_PARAMS = {
    'topology': 'ring',
    'max_delay_sec': 5.0,
    'refractory_pct': 30,
    'variation': 0.1,
}

SEED = 42
DURATION_SEC = 3600  # 1 hour simulation


def load_ai_recommendations(recommendations_file='models/parameter_recommendations.csv'):
    """Load AI recommendations from CSV."""
    df = pd.read_csv(recommendations_file)
    print(f"✓ Loaded {len(df)} AI recommendations")
    return df


def create_baseline_coordinator(n_presses, mix, topology, variation=0.1, seed=None):
    """
    Create a baseline coordinator (no coordination, max_delay=0).

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        topology: Network topology (ignored for baseline)
        variation: Random variation
        seed: Random seed

    Returns:
        CardiacCoordinator with coordination disabled
    """
    power_profiles = create_press_fleet(n_presses, mix, variation, seed)

    press_configs = []
    for i, profile in enumerate(power_profiles):
        press_id = f"Press_{chr(65+i)}"
        config = PressConfig(
            press_id=press_id,
            power_profile=profile,
            max_delay_sec=0.0,  # NO COORDINATION
        )
        press_configs.append(config)

    return CardiacCoordinator(press_configs, topology, seed)


def create_static_coordinator(n_presses, mix, params, seed=None):
    """
    Create a static cardiac coordinator with default parameters.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        params: Parameter dict with topology, max_delay_sec, refractory_pct, variation
        seed: Random seed

    Returns:
        CardiacCoordinator with static parameters
    """
    power_profiles = create_press_fleet(
        n_presses, mix, params['variation'], seed
    )

    press_configs = []
    for i, profile in enumerate(power_profiles):
        press_id = f"Press_{chr(65+i)}"
        config = PressConfig(
            press_id=press_id,
            power_profile=profile,
            max_delay_sec=params['max_delay_sec'],
        )
        press_configs.append(config)

    coord = CardiacCoordinator(press_configs, params['topology'], seed)
    coord.refractory_pct = params['refractory_pct']

    return coord


def create_ai_coordinator(n_presses, mix, ai_params, seed=None):
    """
    Create an AI-optimized cardiac coordinator.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        ai_params: AI-recommended parameters
        seed: Random seed

    Returns:
        CardiacCoordinator with AI-optimized parameters
    """
    power_profiles = create_press_fleet(
        n_presses, mix, ai_params['variation'], seed
    )

    press_configs = []
    for i, profile in enumerate(power_profiles):
        press_id = f"Press_{chr(65+i)}"
        config = PressConfig(
            press_id=press_id,
            power_profile=profile,
            max_delay_sec=ai_params['max_delay_sec'],
        )
        press_configs.append(config)

    coord = CardiacCoordinator(press_configs, ai_params['topology'], seed)
    coord.refractory_pct = ai_params['refractory_pct']

    return coord


def run_single_simulation(coordinator, duration_sec, verbose=False):
    """Run a single simulation and return results."""
    engine = SimulationEngine(coordinator)
    results = engine.run(
        duration_sec=duration_sec,
        dt=0.5,
        verbose=verbose
    )
    return results


def extract_summary_metrics(results):
    """Extract key metrics from simulation results."""
    history = results['history']
    aggregate_power = np.array(history['aggregate_power'])
    time_steps = np.array(history['time'])

    # Calculate peak power
    peak_power = np.max(aggregate_power)

    # Calculate 15-min rolling average peak
    window_sec = 900  # 15 minutes
    dt = time_steps[1] - time_steps[0]
    window_size = int(window_sec / dt)

    if len(aggregate_power) >= window_size:
        rolling_avg = np.convolve(
            aggregate_power,
            np.ones(window_size)/window_size,
            mode='valid'
        )
        peak_15min = np.max(rolling_avg)
    else:
        peak_15min = peak_power

    # Mean power
    mean_power = np.mean(aggregate_power)

    return {
        'peak_power': float(peak_power),
        'peak_15min': float(peak_15min),
        'mean_power': float(mean_power),
    }


def run_scenario_comparison(n_presses, mix, ai_recommendations_df, seed=42, duration_sec=3600):
    """
    Run all three methods for a single scenario.

    Returns:
        Dict with results for baseline, static, and ai methods
    """
    print(f"\n{'='*70}")
    print(f"SCENARIO: {n_presses} presses, {mix} mix")
    print(f"{'='*70}")

    # Get AI recommendations for this scenario
    ai_row = ai_recommendations_df[
        (ai_recommendations_df['n_presses'] == n_presses) &
        (ai_recommendations_df['mix'] == mix)
    ]

    if len(ai_row) == 0:
        print(f"❌ No AI recommendations found for {n_presses}p {mix}")
        return None

    ai_params = {
        'topology': ai_row['topology'].values[0],
        'max_delay_sec': float(ai_row['max_delay_sec'].values[0]),
        'refractory_pct': int(ai_row['refractory_pct'].values[0]),
        'variation': float(ai_row['variation'].values[0]),
    }

    print(f"\n📋 Parameters:")
    print(f"  Static: topology={STATIC_PARAMS['topology']}, "
          f"max_delay={STATIC_PARAMS['max_delay_sec']}s, "
          f"refractory={STATIC_PARAMS['refractory_pct']}%, "
          f"variation={STATIC_PARAMS['variation']}")
    print(f"  AI-Opt: topology={ai_params['topology']}, "
          f"max_delay={ai_params['max_delay_sec']}s, "
          f"refractory={ai_params['refractory_pct']}%, "
          f"variation={ai_params['variation']}")

    results = {}

    # 1. Baseline (no coordination)
    print(f"\n  [1/3] Running baseline (no coordination)...")
    start_time = time.time()
    baseline_coord = create_baseline_coordinator(
        n_presses, mix, 'ring', STATIC_PARAMS['variation'], seed
    )
    baseline_results = run_single_simulation(baseline_coord, duration_sec)
    results['baseline'] = {
        'full_results': baseline_results,
        'summary': extract_summary_metrics(baseline_results),
        'params': {'max_delay_sec': 0.0, 'coordination': False},
        'runtime_sec': time.time() - start_time,
    }
    print(f"    ✓ Peak: {results['baseline']['summary']['peak_power']:.1f} kW "
          f"({results['baseline']['runtime_sec']:.1f}s)")

    # 2. Static cardiac (default params)
    print(f"  [2/3] Running static cardiac (default params)...")
    start_time = time.time()
    static_coord = create_static_coordinator(n_presses, mix, STATIC_PARAMS, seed)
    static_results = run_single_simulation(static_coord, duration_sec)
    results['static'] = {
        'full_results': static_results,
        'summary': extract_summary_metrics(static_results),
        'params': STATIC_PARAMS.copy(),
        'runtime_sec': time.time() - start_time,
    }
    print(f"    ✓ Peak: {results['static']['summary']['peak_power']:.1f} kW "
          f"({results['static']['runtime_sec']:.1f}s)")

    # 3. AI-optimized cardiac
    print(f"  [3/3] Running AI-optimized cardiac...")
    start_time = time.time()
    ai_coord = create_ai_coordinator(n_presses, mix, ai_params, seed)
    ai_results = run_single_simulation(ai_coord, duration_sec)
    results['ai'] = {
        'full_results': ai_results,
        'summary': extract_summary_metrics(ai_results),
        'params': ai_params.copy(),
        'runtime_sec': time.time() - start_time,
    }
    print(f"    ✓ Peak: {results['ai']['summary']['peak_power']:.1f} kW "
          f"({results['ai']['runtime_sec']:.1f}s)")

    # Calculate improvements
    baseline_peak = results['baseline']['summary']['peak_power']
    static_peak = results['static']['summary']['peak_power']
    ai_peak = results['ai']['summary']['peak_power']

    static_reduction = (baseline_peak - static_peak) / baseline_peak * 100
    ai_reduction = (baseline_peak - ai_peak) / baseline_peak * 100
    ai_improvement = ai_reduction - static_reduction

    print(f"\n  📊 Results:")
    print(f"    Baseline:  {baseline_peak:.1f} kW")
    print(f"    Static:    {static_peak:.1f} kW ({static_reduction:+.1f}%)")
    print(f"    AI-Opt:    {ai_peak:.1f} kW ({ai_reduction:+.1f}%)")
    print(f"    AI Gain:   {ai_improvement:+.1f}% improvement")

    return results


def main():
    """Generate all preloaded results."""
    print("=" * 70)
    print("AI SHOWCASE APP: Preload Results")
    print("=" * 70)
    print(f"Seed: {SEED}")
    print(f"Duration: {DURATION_SEC/60:.0f} minutes per simulation")
    print(f"Scenarios: 15 (5 press counts × 3 mixes)")
    print(f"Methods per scenario: 3 (baseline, static, AI)")
    print(f"Total simulations: 45")
    print("=" * 70)

    # Load AI recommendations
    ai_recommendations = load_ai_recommendations()

    # Define all scenarios
    press_counts = [4, 5, 6, 7, 8]
    mixes = ['realistic', 'varied', 'uniform']

    # Store all results
    all_results = {}
    summary_data = []

    total_scenarios = len(press_counts) * len(mixes)
    scenario_num = 0
    overall_start = time.time()

    # Run all scenarios
    for n_presses in press_counts:
        for mix in mixes:
            scenario_num += 1
            print(f"\n\n{'#'*70}")
            print(f"# SCENARIO {scenario_num}/{total_scenarios}")
            print(f"{'#'*70}")

            scenario_key = f"{n_presses}p_{mix}"

            results = run_scenario_comparison(
                n_presses, mix, ai_recommendations, SEED, DURATION_SEC
            )

            if results is None:
                continue

            all_results[scenario_key] = results

            # Add to summary
            summary_data.append({
                'scenario': scenario_key,
                'n_presses': n_presses,
                'mix': mix,
                'baseline_peak': results['baseline']['summary']['peak_power'],
                'static_peak': results['static']['summary']['peak_power'],
                'ai_peak': results['ai']['summary']['peak_power'],
                'static_reduction_pct': (
                    (results['baseline']['summary']['peak_power'] -
                     results['static']['summary']['peak_power']) /
                    results['baseline']['summary']['peak_power'] * 100
                ),
                'ai_reduction_pct': (
                    (results['baseline']['summary']['peak_power'] -
                     results['ai']['summary']['peak_power']) /
                    results['baseline']['summary']['peak_power'] * 100
                ),
                'ai_improvement_pct': (
                    ((results['baseline']['summary']['peak_power'] -
                      results['ai']['summary']['peak_power']) /
                     results['baseline']['summary']['peak_power'] * 100) -
                    ((results['baseline']['summary']['peak_power'] -
                      results['static']['summary']['peak_power']) /
                     results['baseline']['summary']['peak_power'] * 100)
                ),
            })

    total_time = time.time() - overall_start

    print("\n\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)

    # Create output directory
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)

    # Save full results as pickle
    pkl_path = output_dir / 'showcase_results.pkl'
    with open(pkl_path, 'wb') as f:
        pickle.dump(all_results, f)
    print(f"✓ Saved full results: {pkl_path}")
    print(f"  Size: {pkl_path.stat().st_size / 1024:.1f} KB")

    # Save summary as JSON and CSV
    summary_df = pd.DataFrame(summary_data)

    json_path = output_dir / 'showcase_summary.json'
    summary_df.to_json(json_path, orient='records', indent=2)
    print(f"✓ Saved summary (JSON): {json_path}")

    csv_path = output_dir / 'showcase_summary.csv'
    summary_df.to_csv(csv_path, index=False)
    print(f"✓ Saved summary (CSV): {csv_path}")

    # Save metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'seed': SEED,
        'duration_sec': DURATION_SEC,
        'num_scenarios': len(all_results),
        'total_simulations': len(all_results) * 3,
        'total_runtime_sec': total_time,
        'static_params': STATIC_PARAMS,
    }

    meta_path = output_dir / 'metadata.json'
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved metadata: {meta_path}")

    print("\n" + "=" * 70)
    print("✅ PRELOAD COMPLETE!")
    print("=" * 70)
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Scenarios: {len(all_results)}")
    print(f"Total simulations: {len(all_results) * 3}")
    print(f"\nSummary statistics:")
    print(f"  Static reduction: {summary_df['static_reduction_pct'].mean():.1f}% ± {summary_df['static_reduction_pct'].std():.1f}%")
    print(f"  AI reduction:     {summary_df['ai_reduction_pct'].mean():.1f}% ± {summary_df['ai_reduction_pct'].std():.1f}%")
    print(f"  AI improvement:   {summary_df['ai_improvement_pct'].mean():.1f}% ± {summary_df['ai_improvement_pct'].std():.1f}%")
    print(f"\nFiles saved to: {output_dir}")
    print(f"  - showcase_results.pkl (full results)")
    print(f"  - showcase_summary.json (summary)")
    print(f"  - showcase_summary.csv (summary)")
    print(f"  - metadata.json (metadata)")


if __name__ == "__main__":
    main()
