"""
AI Recommendation Validation Script

Validates AI-recommended parameters by comparing them against Phase 5 baseline.
Runs simulations with both parameter sets and measures improvement.

Usage:
    # Validate all scenarios (15 scenarios × 5 seeds = 75 simulations)
    python scripts/validate_ai_recommendations.py

    # Validate specific scenario
    python scripts/validate_ai_recommendations.py --n-presses 7 --mix realistic --seeds 5

    # Quick test (fewer seeds)
    python scripts/validate_ai_recommendations.py --seeds 3
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import (
    ScenarioConfig,
    run_scenario,
    run_batch,
    compare_single_scenario
)


# Phase 5 baseline parameters (static for all scenarios)
BASELINE_PARAMS = {
    'topology': 'ring',
    'max_delay_sec': 5.0,
    'refractory_pct': 30,
    'variation': 0.1,
}


def load_ai_recommendations(recommendations_file='models/parameter_recommendations.csv'):
    """Load AI recommendations from CSV."""
    df = pd.read_csv(recommendations_file)
    print(f"✓ Loaded {len(df)} AI recommendations")
    return df


def create_scenario_configs(n_presses, mix, params, seeds, duration_sec=3600):
    """Create ScenarioConfig objects for testing."""
    configs = []

    for seed in seeds:
        config = ScenarioConfig(
            n_presses=n_presses,
            mix=mix,
            topology=params['topology'],
            duration_sec=duration_sec,
            max_delay_sec=params['max_delay_sec'],
            variation=params['variation'],
            seed=seed,
            name=f"val_{n_presses}p_{mix}_{params['topology']}_s{seed}"
        )
        config.refractory_pct = params['refractory_pct']
        configs.append(config)

    return configs


def run_comparison(n_presses, mix, ai_params, baseline_params, seeds, parallel=True):
    """
    Run simulations with both AI and baseline parameters.

    Returns:
        results: Dict with baseline and AI results
    """
    print(f"\n{'='*70}")
    print(f"VALIDATING: {n_presses} presses, {mix} mix")
    print(f"{'='*70}")

    print(f"\n📊 Baseline Parameters (Phase 5):")
    print(f"   Topology: {baseline_params['topology']}")
    print(f"   Max Delay: {baseline_params['max_delay_sec']}s")
    print(f"   Refractory: {baseline_params['refractory_pct']}%")
    print(f"   Variation: {baseline_params['variation']}")

    print(f"\n🤖 AI-Recommended Parameters:")
    print(f"   Topology: {ai_params['topology']}")
    print(f"   Max Delay: {ai_params['max_delay_sec']}s")
    print(f"   Refractory: {ai_params['refractory_pct']}%")
    print(f"   Variation: {ai_params['variation']}")

    # Create configs
    baseline_configs = create_scenario_configs(n_presses, mix, baseline_params, seeds)
    ai_configs = create_scenario_configs(n_presses, mix, ai_params, seeds)

    print(f"\n🚀 Running simulations ({len(seeds)} seeds each)...")

    # Run baseline
    print(f"\n   Running baseline simulations...")
    baseline_results = run_batch(baseline_configs, parallel=parallel, verbose=False)

    # Run AI
    print(f"   Running AI simulations...")
    ai_results = run_batch(ai_configs, parallel=parallel, verbose=False)

    # Analyze results
    baseline_metrics = analyze_results(baseline_results, "Baseline")
    ai_metrics = analyze_results(ai_results, "AI")

    # Calculate improvement
    improvement = {
        'peak_reduction_improvement': ai_metrics['mean_peak_reduction'] - baseline_metrics['mean_peak_reduction'],
        'win_rate_improvement': ai_metrics['win_rate'] - baseline_metrics['win_rate'],
        'savings_improvement': ai_metrics['mean_savings'] - baseline_metrics['mean_savings'],
    }

    print(f"\n{'='*70}")
    print(f"RESULTS COMPARISON")
    print(f"{'='*70}")

    print(f"\n📈 Performance Metrics:")
    print(f"{'':20s} {'Baseline':>15s} {'AI':>15s} {'Improvement':>15s}")
    print(f"{'-'*70}")
    print(f"{'Win Rate':20s} {baseline_metrics['win_rate']:>14.1f}% {ai_metrics['win_rate']:>14.1f}% {improvement['win_rate_improvement']:>14.1f}%")
    print(f"{'Peak Reduction':20s} {baseline_metrics['mean_peak_reduction']:>14.1f}% {ai_metrics['mean_peak_reduction']:>14.1f}% {improvement['peak_reduction_improvement']:>14.1f}%")
    print(f"{'Annual Savings':20s} ${baseline_metrics['mean_savings']:>13.0f} ${ai_metrics['mean_savings']:>13.0f} ${improvement['savings_improvement']:>13.0f}")

    # Statistical significance
    if len(seeds) >= 5:
        from scipy import stats
        baseline_peaks = [compare_single_scenario(r)['comparison']['peak_reduction_pct'] for r in baseline_results]
        ai_peaks = [compare_single_scenario(r)['comparison']['peak_reduction_pct'] for r in ai_results]
        t_stat, p_value = stats.ttest_ind(ai_peaks, baseline_peaks)

        print(f"\n📊 Statistical Test (t-test):")
        print(f"   p-value: {p_value:.4f}")
        if p_value < 0.05:
            print(f"   ✅ Statistically significant improvement (p < 0.05)")
        else:
            print(f"   ⚠️  Not statistically significant (p >= 0.05)")

    return {
        'n_presses': n_presses,
        'mix': mix,
        'baseline': baseline_metrics,
        'ai': ai_metrics,
        'improvement': improvement,
        'baseline_results': baseline_results,
        'ai_results': ai_results,
    }


def analyze_results(results, label):
    """Analyze batch of results and compute metrics."""
    comparisons = [compare_single_scenario(r) for r in results]

    wins = sum(1 for c in comparisons if c['comparison']['cardiac_wins'])
    win_rate = (wins / len(results)) * 100

    peak_reductions = [c['comparison']['peak_reduction_pct'] for c in comparisons]
    mean_peak_reduction = np.mean(peak_reductions)
    std_peak_reduction = np.std(peak_reductions)

    savings = [c['cost_savings']['annual_savings_usd'] for c in comparisons]
    mean_savings = np.mean(savings)

    metrics = {
        'win_rate': win_rate,
        'mean_peak_reduction': mean_peak_reduction,
        'std_peak_reduction': std_peak_reduction,
        'mean_savings': mean_savings,
        'min_peak_reduction': min(peak_reductions),
        'max_peak_reduction': max(peak_reductions),
    }

    return metrics


def validate_all_scenarios(recommendations_df, seeds, parallel=True):
    """Validate AI recommendations for all scenarios."""
    print("\n" + "="*70)
    print("VALIDATING ALL AI RECOMMENDATIONS")
    print("="*70)
    print(f"\nTotal scenarios: {len(recommendations_df)}")
    print(f"Seeds per scenario: {len(seeds)}")
    print(f"Total simulations: {len(recommendations_df) * len(seeds) * 2} (baseline + AI)")

    all_results = []

    for idx, row in recommendations_df.iterrows():
        n_presses = int(row['n_presses'])
        mix = row['mix']

        ai_params = {
            'topology': row['topology'],
            'max_delay_sec': row['max_delay_sec'],
            'refractory_pct': int(row['refractory_pct']),
            'variation': row['variation'],
        }

        result = run_comparison(
            n_presses, mix, ai_params, BASELINE_PARAMS, seeds, parallel
        )
        all_results.append(result)

    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    summary_data = []
    for result in all_results:
        summary_data.append({
            'n_presses': result['n_presses'],
            'mix': result['mix'],
            'baseline_win_rate': result['baseline']['win_rate'],
            'ai_win_rate': result['ai']['win_rate'],
            'win_rate_improvement': result['improvement']['win_rate_improvement'],
            'baseline_peak_reduction': result['baseline']['mean_peak_reduction'],
            'ai_peak_reduction': result['ai']['mean_peak_reduction'],
            'peak_reduction_improvement': result['improvement']['peak_reduction_improvement'],
        })

    summary_df = pd.DataFrame(summary_data)

    print(f"\n{summary_df.to_string(index=False)}")

    # Overall statistics
    print(f"\n📊 Overall Statistics:")
    print(f"   Scenarios with improved win rate: {sum(1 for x in all_results if x['improvement']['win_rate_improvement'] > 0)}/{len(all_results)}")
    print(f"   Scenarios with improved peak reduction: {sum(1 for x in all_results if x['improvement']['peak_reduction_improvement'] > 0)}/{len(all_results)}")
    print(f"   Mean win rate improvement: {summary_df['win_rate_improvement'].mean():.1f}%")
    print(f"   Mean peak reduction improvement: {summary_df['peak_reduction_improvement'].mean():.1f}%")

    # Save results
    output_dir = Path('results/validation')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = output_dir / f"validation_summary_{timestamp}.csv"
    summary_df.to_csv(summary_file, index=False)

    print(f"\n✓ Saved validation summary to {summary_file}")

    return all_results, summary_df


def main():
    parser = argparse.ArgumentParser(
        description='Validate AI parameter recommendations against baseline'
    )

    parser.add_argument(
        '--recommendations',
        type=str,
        default='models/parameter_recommendations.csv',
        help='Path to AI recommendations CSV'
    )

    parser.add_argument(
        '--n-presses',
        type=int,
        help='Validate specific press count only'
    )

    parser.add_argument(
        '--mix',
        type=str,
        choices=['realistic', 'varied', 'uniform'],
        help='Validate specific mix only'
    )

    parser.add_argument(
        '--seeds',
        type=int,
        default=5,
        help='Number of random seeds to test (default: 5)'
    )

    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run sequentially (for debugging)'
    )

    args = parser.parse_args()

    print("="*70)
    print("AI RECOMMENDATION VALIDATION")
    print("="*70)

    # Load recommendations
    recommendations_df = load_ai_recommendations(args.recommendations)

    # Filter if specific scenario requested
    if args.n_presses or args.mix:
        if args.n_presses:
            recommendations_df = recommendations_df[recommendations_df['n_presses'] == args.n_presses]
        if args.mix:
            recommendations_df = recommendations_df[recommendations_df['mix'] == args.mix]

        print(f"\n⚠️  Filtered to {len(recommendations_df)} scenario(s)")

    # Generate seeds
    seeds = list(range(42, 42 + args.seeds))

    # Validate
    all_results, summary_df = validate_all_scenarios(
        recommendations_df,
        seeds,
        parallel=not args.sequential
    )

    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print()


if __name__ == "__main__":
    main()
