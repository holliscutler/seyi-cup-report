"""
Comprehensive Cardiac Coordination Test Suite

Tests 4-8 presses × 20 seeds × 1 hour each = 100 total scenarios.

This comprehensive test evaluates:
- Power distribution across press counts
- Cost savings
- Aggregate power demand
- Coordination effectiveness
- Scalability

Usage:
    python tests/test_comprehensive.py                    # Run all tests (parallel)
    python tests/test_comprehensive.py --sequential       # Run sequentially
    python tests/test_comprehensive.py --workers 4        # Custom worker count
    python tests/test_comprehensive.py --quick            # Quick test (10 min instead of 1 hour)
"""

import sys
import os
import argparse
from datetime import datetime
from test_framework import (
    create_scenario_grid,
    run_batch,
    save_results,
    compare_across_press_counts,
    generate_json_report,
    generate_csv_summary,
    generate_markdown_report,
    generate_summary_table,
)


def test_press_scaling_comprehensive(
    presses_list: list = [4, 5, 6, 7, 8],
    n_seeds: int = 20,
    duration_hours: float = 1.0,
    parallel: bool = True,
    max_workers: int = None,
    output_prefix: str = "comprehensive"
):
    """
    Comprehensive test of cardiac coordination across press counts and seeds.

    Args:
        presses_list: List of press counts to test
        n_seeds: Number of seeds to test per press count
        duration_hours: Duration of each simulation in hours
        parallel: Run scenarios in parallel
        max_workers: Maximum parallel workers (None = CPU count)
        output_prefix: Prefix for output files
    """
    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join("results", f"run_{timestamp}")
    os.makedirs(results_dir, exist_ok=True)

    print("\n" + "="*80)
    print("COMPREHENSIVE CARDIAC COORDINATION TEST")
    print("="*80)
    print(f"  Press Counts: {presses_list}")
    print(f"  Seeds per count: {n_seeds}")
    print(f"  Duration per simulation: {duration_hours} hours ({duration_hours*60} minutes)")
    print(f"  Total scenarios: {len(presses_list) * n_seeds}")
    print(f"  Parallel execution: {parallel}")
    if parallel and max_workers:
        print(f"  Max workers: {max_workers}")
    print(f"  Output directory: {results_dir}")
    print("="*80 + "\n")

    # Generate scenario grid
    seeds = list(range(42, 42 + n_seeds))  # Start from seed 42
    duration_sec = duration_hours * 3600

    print("Generating scenario grid...")
    scenarios = create_scenario_grid(
        presses_list=presses_list,
        seeds=seeds,
        mix='realistic',
        topology='all_to_all',  # Changed from 'ring' to give each press full visibility
        duration_sec=duration_sec,
        max_delay_sec=5.0,
        variation=0.1
    )

    print(f"✓ Generated {len(scenarios)} scenarios\n")

    # Run all scenarios
    print("Running simulations...")
    print(f"  (This will take a while with {duration_hours}-hour simulations)\n")

    results = run_batch(
        scenarios,
        parallel=parallel,
        max_workers=max_workers,
        verbose=True
    )

    print(f"\n✓ All {len(results)} scenarios complete!\n")

    # Save raw results (pickle format for full data)
    results_file = os.path.join(results_dir, f"{output_prefix}_results.pkl")
    print(f"Saving raw results to {results_file}...")
    save_results(results, results_file, format='pickle')

    # Analyze results
    print("\nAnalyzing results...")
    scaling_analysis = compare_across_press_counts(results)

    # Generate reports
    print("\nGenerating reports...")

    # 1. JSON report (full data)
    json_file = os.path.join(results_dir, f"{output_prefix}_report.json")
    generate_json_report(scaling_analysis, json_file)

    # 2. CSV summary (for spreadsheets)
    csv_file = os.path.join(results_dir, f"{output_prefix}_summary.csv")
    generate_csv_summary(scaling_analysis, csv_file)

    # 3. Markdown report (human-readable)
    md_file = os.path.join(results_dir, f"{output_prefix}_report.md")
    generate_markdown_report(
        scaling_analysis,
        md_file,
        title="Comprehensive Cardiac Coordination Test - Press Scaling Analysis"
    )

    # 4. Console summary
    print(generate_summary_table(scaling_analysis))

    print("\n" + "="*80)
    print("COMPREHENSIVE TEST COMPLETE")
    print("="*80)
    print(f"  Output directory: {results_dir}")
    print(f"  Results pickle: {results_file}")
    print(f"  JSON report: {json_file}")
    print(f"  CSV summary: {csv_file}")
    print(f"  Markdown report: {md_file}")
    print("="*80 + "\n")

    return results, scaling_analysis


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Comprehensive cardiac coordination test suite'
    )

    parser.add_argument(
        '--presses',
        type=int,
        nargs='+',
        default=[4, 5, 6, 7, 8],
        help='List of press counts to test (default: 4 5 6 7 8)'
    )

    parser.add_argument(
        '--seeds',
        type=int,
        default=20,
        help='Number of seeds per press count (default: 20)'
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=1.0,
        help='Duration per simulation in hours (default: 1.0)'
    )

    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run scenarios sequentially instead of in parallel'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Maximum parallel workers (default: CPU count)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='comprehensive',
        help='Output file prefix (default: comprehensive)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test: 10-minute simulations instead of 1 hour'
    )

    args = parser.parse_args()

    # Adjust duration for quick test
    duration = args.duration
    if args.quick:
        duration = 10.0 / 60.0  # 10 minutes in hours
        print("\n⚡ QUICK TEST MODE: Using 10-minute simulations\n")

    # Run comprehensive test
    results, analysis = test_press_scaling_comprehensive(
        presses_list=args.presses,
        n_seeds=args.seeds,
        duration_hours=duration,
        parallel=not args.sequential,
        max_workers=args.workers,
        output_prefix=args.output
    )

    return results, analysis


if __name__ == "__main__":
    results, analysis = main()
