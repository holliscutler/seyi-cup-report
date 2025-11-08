"""
Training Data Generation Script

Runs simulations for all scenarios in parallel and saves results.

Usage:
    # Run all scenarios from grid
    python scripts/generate_training_data.py --scenario-file data/scenarios/scenario_grid_v1.json

    # Run in batches (safer for memory)
    python scripts/generate_training_data.py --scenario-file data/scenarios/scenario_grid_v1.json --batch-size 100

    # Sequential execution (for debugging)
    python scripts/generate_training_data.py --scenario-file data/scenarios/scenario_grid_v1.json --sequential
"""

import sys
import os
import json
import argparse
import pickle
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import (
    ScenarioConfig,
    run_scenario,
    run_batch,
    compare_single_scenario,
    save_results
)


def load_scenario_grid(scenario_file):
    """Load scenario grid from JSON."""
    with open(scenario_file, 'r') as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    scenarios = data.get('scenarios', [])

    print(f"Loaded {len(scenarios)} scenarios")
    print(f"  Version: {metadata.get('version', 'unknown')}")
    print(f"  Generated: {metadata.get('generated_at', 'unknown')}")

    return scenarios, metadata


def scenarios_to_configs(scenarios):
    """Convert scenario dicts to ScenarioConfig objects."""
    configs = []

    for scenario in scenarios:
        config = ScenarioConfig(
            n_presses=scenario['n_presses'],
            mix=scenario['mix'],
            topology=scenario['topology'],
            duration_sec=scenario['duration_sec'],
            max_delay_sec=scenario['max_delay_sec'],
            variation=scenario['variation'],
            seed=scenario['seed'],
            name=scenario['name']
        )

        # Store additional fields for later reference
        config.scenario_id = scenario.get('id')
        config.version = scenario.get('version')
        config.refractory_pct = scenario.get('refractory_pct', 30)

        configs.append(config)

    return configs


def process_results_to_csv(results, output_file, append=False):
    """
    Process simulation results into CSV format for ML training.

    Args:
        results: List of ScenarioResult objects
        output_file: Output CSV file path
        append: If True, append to existing file (default: False)
    """
    rows = []

    for result in results:
        # Get comparison metrics
        comparison = compare_single_scenario(result)
        comp = comparison['comparison']
        cost = comparison['cost_savings']
        coord = comparison['coordination']

        # Features (X)
        row = {
            # Press configuration
            'n_presses': result.config.n_presses,
            'mix': result.config.mix,
            'topology': result.config.topology,
            'seed': result.config.seed,

            # Coordination parameters (what we're optimizing)
            'max_delay_sec': result.config.max_delay_sec,
            'refractory_pct': getattr(result.config, 'refractory_pct', 30),
            'variation': result.config.variation,

            # Targets (y) - what we measure
            'cardiac_wins': comp['cardiac_wins'],
            'win_rate': 100.0 if comp['cardiac_wins'] else 0.0,  # Binary for this run
            'peak_reduction_pct': comp['peak_reduction_pct'],
            'baseline_peak_kw': comp['baseline_peak_kw'],
            'cardiac_peak_kw': comp['cardiac_peak_kw'],
            'energy_change_kwh': comp['energy_change_kwh'],
            'annual_savings_usd': cost['annual_savings_usd'],

            # Coordination activity
            'total_delays': coord['total_delays'],
            'collisions_avoided': coord['total_collisions_avoided'],

            # Metadata
            'duration_sec': result.config.duration_sec,
            'scenario_name': result.config.name,
        }

        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Save to CSV (append or overwrite)
    if append and os.path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)

    print(f"\n✓ Processed {len(rows)} results to CSV")
    print(f"  Output: {output_file}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Shape: {df.shape}")

    # Print summary statistics
    print(f"\n📊 Summary Statistics:")
    print(f"  Win rate: {df['cardiac_wins'].sum() / len(df) * 100:.1f}%")
    print(f"  Mean peak reduction: {df['peak_reduction_pct'].mean():.2f}%")
    print(f"  Peak reduction range: [{df['peak_reduction_pct'].min():.1f}%, {df['peak_reduction_pct'].max():.1f}%]")

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Generate AI training data by running simulations'
    )

    parser.add_argument(
        '--scenario-file',
        type=str,
        required=True,
        help='JSON file containing scenario grid'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Directory to save raw results (default: data/raw)'
    )

    parser.add_argument(
        '--processed-dir',
        type=str,
        default='data/processed',
        help='Directory to save processed CSV (default: data/processed)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Process in batches of this size (default: all at once)'
    )

    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run sequentially instead of parallel (for debugging)'
    )

    parser.add_argument(
        '--max-workers',
        type=int,
        default=None,
        help='Maximum parallel workers (default: CPU count)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit to first N scenarios (for testing)'
    )

    parser.add_argument(
        '--csv-only',
        action='store_true',
        help='Only generate CSV, skip pickle files (saves ~20 GB disk space)'
    )

    args = parser.parse_args()

    # Resolve paths
    project_root = Path(__file__).parent.parent
    scenario_path = project_root / args.scenario_file
    output_dir = project_root / args.output_dir
    processed_dir = project_root / args.processed_dir

    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("TRAINING DATA GENERATION")
    print("=" * 70)
    print(f"Scenario file: {scenario_path}")
    print(f"Output directory: {output_dir}")
    print(f"Parallel: {not args.sequential}")
    if args.max_workers:
        print(f"Max workers: {args.max_workers}")
    if args.batch_size:
        print(f"Batch size: {args.batch_size}")
    if args.limit:
        print(f"Limit: {args.limit} scenarios")
    if args.csv_only:
        print(f"Mode: CSV-only (skipping pickle files, saves ~20 GB)")
    print("=" * 70 + "\n")

    # Load scenario grid
    scenarios, metadata = load_scenario_grid(scenario_path)

    # Limit if requested
    if args.limit:
        scenarios = scenarios[:args.limit]
        print(f"⚠️  Limited to first {args.limit} scenarios\n")

    # Convert to configs
    configs = scenarios_to_configs(scenarios)

    print(f"\n🚀 Running {len(configs)} simulations...\n")

    # Generate timestamp for output files (do this early)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = metadata.get('version', 'v1')
    csv_file = processed_dir / f"training_data_{version}_{timestamp}.csv"

    # Determine batching
    if args.batch_size and len(configs) > args.batch_size:
        # Run in batches
        num_batches = (len(configs) + args.batch_size - 1) // args.batch_size
        print(f"Running in {num_batches} batches of {args.batch_size}")

        if args.csv_only:
            print(f"💡 CSV-only mode: Processing batches incrementally to save memory\n")
        else:
            print()

        all_results = [] if not args.csv_only else None  # Don't accumulate in csv-only mode

        for batch_num in range(num_batches):
            start_idx = batch_num * args.batch_size
            end_idx = min((batch_num + 1) * args.batch_size, len(configs))
            batch_configs = configs[start_idx:end_idx]

            print(f"Batch {batch_num + 1}/{num_batches} ({len(batch_configs)} scenarios)...")

            # Run batch
            batch_results = run_batch(
                batch_configs,
                parallel=not args.sequential,
                max_workers=args.max_workers,
                verbose=True
            )

            # Process batch immediately in csv-only mode (saves memory!)
            if args.csv_only:
                # Append batch to CSV immediately
                process_results_to_csv(batch_results, str(csv_file), append=(batch_num > 0))
                print(f"✓ Batch processed to CSV (memory freed)\n")
                # Don't keep results in memory
            else:
                # Accumulate results for later processing
                all_results.extend(batch_results)

                # Save batch pickle
                batch_file = output_dir / f"batch_{batch_num + 1:03d}_results.pkl"
                save_results(batch_results, str(batch_file), format='pickle')
                print(f"✓ Saved batch to {batch_file}\n")

        results = all_results if all_results is not None else []
    else:
        # Run all at once
        results = run_batch(
            configs,
            parallel=not args.sequential,
            max_workers=args.max_workers,
            verbose=True
        )

    print(f"\n✓ All {len(configs)} simulations complete!\n")

    # Save complete results (pickle) - unless csv-only mode
    if not args.csv_only and len(results) > 0:
        results_file = output_dir / f"training_data_{version}_{timestamp}.pkl"
        save_results(results, str(results_file), format='pickle')
        print(f"✓ Saved complete results to {results_file}")
    else:
        results_file = None
        if args.csv_only:
            print(f"⚡ Skipped pickle file (csv-only mode)")

    # Process to CSV for ML training (unless already done incrementally)
    if not args.csv_only or len(results) > 0:
        # Need to process results to CSV
        df = process_results_to_csv(results, str(csv_file))
    else:
        # CSV already created incrementally during batches
        df = pd.read_csv(str(csv_file))
        print(f"\n✓ CSV already processed incrementally ({len(df)} rows)")
        print(f"  Output: {csv_file}")

    # Save metadata
    metadata_file = processed_dir / f"training_data_{version}_{timestamp}_metadata.json"
    output_metadata = {
        'generated_at': timestamp,
        'version': version,
        'scenario_file': str(scenario_path),
        'total_scenarios': len(configs),  # Total scenarios requested
        'scenarios_in_csv': len(df),      # Actual rows in CSV
        'input_metadata': metadata,
        'csv_file': str(csv_file),
        'csv_only_mode': args.csv_only,
    }

    # Add pickle file path if it was saved
    if results_file is not None:
        output_metadata['pickle_file'] = str(results_file)

    with open(metadata_file, 'w') as f:
        json.dump(output_metadata, f, indent=2)

    print(f"✓ Saved metadata to {metadata_file}")

    print("\n" + "=" * 70)
    print("TRAINING DATA GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nFiles created:")
    if results_file is not None:
        print(f"  Raw results: {results_file}")
    print(f"  Training CSV: {csv_file}")
    print(f"  Metadata: {metadata_file}")
    if args.csv_only:
        print(f"\n💾 Disk space saved: ~20 GB (csv-only mode)")
    print(f"\nNext steps:")
    print(f"  1. Analyze data: jupyter notebook or pandas")
    print(f"  2. Train model: see docs/AI_Training_Guide.md")
    print(f"  3. Validate predictions")
    print()


if __name__ == "__main__":
    main()
