"""
Simulation Runner

Handles running scenarios (baseline and cardiac simulations) and collecting results.
Supports single scenarios, batch processing, and parallel execution.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.heart_sim import (
    create_coordinator_auto,
    SimulationEngine,
    MetricsCollector,
)
from src.heart_sim.power_profiles import create_press_fleet
from src.heart_sim.press import PressConfig
from src.heart_sim.coordination import CardiacCoordinator

from .scenarios import ScenarioConfig


@dataclass
class ScenarioResult:
    """
    Results from running a scenario (both baseline and cardiac).

    Attributes:
        config: The scenario configuration
        baseline_results: Full results dict from baseline simulation
        cardiac_results: Full results dict from cardiac simulation
        timestamp: When the scenario was run
        duration_actual_sec: Actual wall-clock time to run
    """
    config: ScenarioConfig
    baseline_results: Dict
    cardiac_results: Dict
    timestamp: str
    duration_actual_sec: float

    def to_dict(self) -> Dict:
        """Convert to dictionary (excludes large results dicts)."""
        return {
            'config': self.config.to_dict(),
            'timestamp': self.timestamp,
            'duration_actual_sec': self.duration_actual_sec,
            # Note: baseline_results and cardiac_results excluded for size
        }


def create_baseline_coordinator(
    n_presses: int,
    mix: str,
    topology: str,
    variation: float = 0.1,
    seed: Optional[int] = None
) -> CardiacCoordinator:
    """
    Create a baseline coordinator (no coordination, max_delay=0).

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        topology: Network topology
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


def run_scenario(
    config: ScenarioConfig,
    verbose: bool = False
) -> ScenarioResult:
    """
    Run a single scenario (both baseline and cardiac).

    Args:
        config: Scenario configuration
        verbose: Print progress messages

    Returns:
        ScenarioResult with both baseline and cardiac results
    """
    import time
    start_time = time.time()

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running: {config.name}")
        print(f"  Presses: {config.n_presses}")
        print(f"  Duration: {config.duration_sec/60:.1f} minutes")
        print(f"  Seed: {config.seed}")
        print(f"{'='*60}")

    # Run baseline (no coordination)
    if verbose:
        print("  Running baseline...")
    baseline_coord = create_baseline_coordinator(
        n_presses=config.n_presses,
        mix=config.mix,
        topology=config.topology,
        variation=config.variation,
        seed=config.seed
    )
    baseline_engine = SimulationEngine(baseline_coord)
    baseline_results = baseline_engine.run(
        duration_sec=config.duration_sec,
        dt=0.5,
        verbose=False
    )

    # Run cardiac (with coordination)
    if verbose:
        print("  Running cardiac...")
    cardiac_coord = create_coordinator_auto(
        n_presses=config.n_presses,
        mix=config.mix,
        topology=config.topology,
        max_delay_sec=config.max_delay_sec,
        variation=config.variation,
        seed=config.seed
    )
    cardiac_engine = SimulationEngine(cardiac_coord)
    cardiac_results = cardiac_engine.run(
        duration_sec=config.duration_sec,
        dt=0.5,
        verbose=False
    )

    end_time = time.time()
    duration_actual = end_time - start_time

    if verbose:
        baseline_peak = baseline_results['history']['aggregate_power'].max() \
            if hasattr(baseline_results['history']['aggregate_power'], 'max') \
            else max(baseline_results['history']['aggregate_power'])
        cardiac_peak = cardiac_results['history']['aggregate_power'].max() \
            if hasattr(cardiac_results['history']['aggregate_power'], 'max') \
            else max(cardiac_results['history']['aggregate_power'])

        print(f"  ✓ Complete in {duration_actual:.1f}s")
        print(f"    Baseline: {baseline_peak:.1f} kW")
        print(f"    Cardiac:  {cardiac_peak:.1f} kW")
        print(f"    Diff:     {cardiac_peak - baseline_peak:+.1f} kW")

    return ScenarioResult(
        config=config,
        baseline_results=baseline_results,
        cardiac_results=cardiac_results,
        timestamp=datetime.now().isoformat(),
        duration_actual_sec=duration_actual
    )


def _run_scenario_worker(config: ScenarioConfig) -> ScenarioResult:
    """Worker function for parallel execution."""
    return run_scenario(config, verbose=False)


def run_batch(
    scenarios: List[ScenarioConfig],
    parallel: bool = False,
    max_workers: Optional[int] = None,
    verbose: bool = True
) -> List[ScenarioResult]:
    """
    Run multiple scenarios in batch.

    Args:
        scenarios: List of scenario configurations
        parallel: Run scenarios in parallel (faster but uses more CPU)
        max_workers: Max parallel workers (default: CPU count)
        verbose: Print progress messages

    Returns:
        List of ScenarioResults
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"BATCH RUN: {len(scenarios)} scenarios")
        print(f"  Parallel: {parallel}")
        if parallel and max_workers:
            print(f"  Workers: {max_workers}")
        print(f"{'='*60}\n")

    results = []

    if parallel:
        # Parallel execution using ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scenarios
            future_to_config = {
                executor.submit(_run_scenario_worker, config): config
                for config in scenarios
            }

            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_config), 1):
                config = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                    if verbose:
                        print(f"  [{i}/{len(scenarios)}] ✓ {config.name}")
                except Exception as e:
                    if verbose:
                        print(f"  [{i}/{len(scenarios)}] ✗ {config.name} - Error: {e}")
    else:
        # Sequential execution
        for i, config in enumerate(scenarios, 1):
            if verbose:
                print(f"  [{i}/{len(scenarios)}] Running {config.name}...")
            result = run_scenario(config, verbose=False)
            results.append(result)
            if verbose:
                print(f"  [{i}/{len(scenarios)}] ✓ Complete")

    if verbose:
        print(f"\n{'='*60}")
        print(f"BATCH COMPLETE: {len(results)}/{len(scenarios)} succeeded")
        print(f"{'='*60}\n")

    return results


def save_results(
    results: List[ScenarioResult],
    filename: str,
    format: str = 'pickle'
):
    """
    Save scenario results to file.

    Args:
        results: List of ScenarioResults
        filename: Output filename
        format: 'pickle' (full results) or 'json' (metadata only)
    """
    if format == 'pickle':
        # Save full results including simulation data
        with open(filename, 'wb') as f:
            pickle.dump(results, f)
        print(f"Results saved to {filename} (pickle format)")

    elif format == 'json':
        # Save metadata only (excludes large simulation results)
        data = {
            'num_scenarios': len(results),
            'timestamp': datetime.now().isoformat(),
            'scenarios': [r.to_dict() for r in results]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Metadata saved to {filename} (JSON format)")

    else:
        raise ValueError(f"Unknown format: {format}. Use 'pickle' or 'json'.")


def load_results(filename: str) -> List[ScenarioResult]:
    """
    Load scenario results from pickle file.

    Args:
        filename: Input filename (pickle)

    Returns:
        List of ScenarioResults
    """
    with open(filename, 'rb') as f:
        results = pickle.load(f)
    print(f"Loaded {len(results)} results from {filename}")
    return results


def filter_results(
    results: List[ScenarioResult],
    n_presses: Optional[int] = None,
    mix: Optional[str] = None,
    topology: Optional[str] = None,
    seed: Optional[int] = None
) -> List[ScenarioResult]:
    """
    Filter results by scenario parameters.

    Args:
        results: List of ScenarioResults
        n_presses: Filter by press count
        mix: Filter by fleet mix
        topology: Filter by topology
        seed: Filter by seed

    Returns:
        Filtered list of ScenarioResults
    """
    filtered = results

    if n_presses is not None:
        filtered = [r for r in filtered if r.config.n_presses == n_presses]

    if mix is not None:
        filtered = [r for r in filtered if r.config.mix == mix]

    if topology is not None:
        filtered = [r for r in filtered if r.config.topology == topology]

    if seed is not None:
        filtered = [r for r in filtered if r.config.seed == seed]

    return filtered
