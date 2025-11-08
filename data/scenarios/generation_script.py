"""
Scenario Grid Generation for AI Training Data Collection

Generates all parameter combinations for systematic exploration.

Usage:
    python data/scenarios/generation_script.py --output scenario_grid_v1.json
    python data/scenarios/generation_script.py --version v2 --expanded
"""

import sys
import os
import json
import argparse
from itertools import product
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.test_framework import ScenarioConfig


def generate_scenario_grid(
    presses_list,
    mixes,
    topologies,
    max_delays,
    refractory_pcts,
    variations,
    seeds,
    duration_sec=3600,
    version='v1'
):
    """
    Generate all parameter combinations.

    Args:
        presses_list: List of press counts [4, 5, 6, 7, 8]
        mixes: List of fleet mixes ['realistic', 'varied', 'uniform']
        topologies: List of topologies ['ring', 'all_to_all']
        max_delays: List of max delays [3, 5, 7]
        refractory_pcts: List of refractory periods [20, 30, 40]
        variations: List of variations [0.05, 0.1, 0.15]
        seeds: List of seeds [42, 43, 44, 45, 46]
        duration_sec: Simulation duration (constant)
        version: Version tag for tracking

    Returns:
        List of scenario configurations
    """
    scenarios = []
    scenario_id = 0

    # Generate all combinations
    for n_presses, mix, topology, max_delay, refractory, variation, seed in product(
        presses_list, mixes, topologies, max_delays, refractory_pcts, variations, seeds
    ):
        scenario_id += 1

        scenario = {
            'id': scenario_id,
            'version': version,
            'n_presses': n_presses,
            'mix': mix,
            'topology': topology,
            'max_delay_sec': max_delay,
            'refractory_pct': refractory,
            'variation': variation,
            'seed': seed,
            'duration_sec': duration_sec,
            'name': f"{version}_p{n_presses}_{mix}_{topology}_d{max_delay}_r{refractory}_v{variation}_s{seed}"
        }

        scenarios.append(scenario)

    return scenarios


def save_scenario_grid(scenarios, output_file, metadata=None):
    """Save scenario grid to JSON with metadata."""

    if metadata is None:
        metadata = {}

    # Add generation info
    metadata.update({
        'generated_at': datetime.now().isoformat(),
        'total_scenarios': len(scenarios),
        'estimated_time_minutes': len(scenarios) / 100 * 0.33,  # ~20s per 100 scenarios
    })

    # Calculate unique combinations
    unique_configs = len(set((s['n_presses'], s['mix'], s['topology'],
                             s['max_delay_sec'], s['refractory_pct'], s['variation'])
                            for s in scenarios))
    metadata['unique_configurations'] = unique_configs
    metadata['seeds_per_config'] = len(scenarios) // unique_configs if unique_configs > 0 else 0

    output = {
        'metadata': metadata,
        'scenarios': scenarios
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Generated {len(scenarios)} scenarios")
    print(f"  Unique configs: {unique_configs}")
    print(f"  Seeds per config: {metadata['seeds_per_config']}")
    print(f"  Estimated time: {metadata['estimated_time_minutes']:.1f} minutes")
    print(f"  Saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate scenario grid for AI training data collection'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='scenario_grid_v1.json',
        help='Output JSON file name (default: scenario_grid_v1.json)'
    )

    parser.add_argument(
        '--version',
        type=str,
        default='v1',
        help='Version tag (default: v1)'
    )

    parser.add_argument(
        '--expanded',
        action='store_true',
        help='Generate expanded grid (more parameters, longer runtime)'
    )

    args = parser.parse_args()

    # Construct full output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, args.output)

    print("=" * 70)
    print("SCENARIO GRID GENERATION")
    print("=" * 70)
    print(f"Version: {args.version}")
    print(f"Mode: {'Expanded' if args.expanded else 'Conservative'}")
    print()

    # Define parameter space
    if args.expanded:
        # Expanded grid (v2+)
        print("Generating EXPANDED grid...")
        presses_list = [4, 5, 6, 7, 8]
        mixes = ['realistic', 'varied', 'uniform', 'small', 'large']
        topologies = ['ring', 'all_to_all', 'line', 'star']
        max_delays = [3, 4, 5, 6, 7]
        refractory_pcts = [20, 30, 40]
        variations = [0.05, 0.1, 0.15]
        seeds = range(42, 47)  # 5 seeds
    else:
        # Conservative grid (v1)
        print("Generating CONSERVATIVE grid...")
        presses_list = [4, 5, 6, 7, 8]
        mixes = ['realistic', 'varied', 'uniform']
        topologies = ['ring', 'all_to_all']
        max_delays = [3, 5, 7]
        refractory_pcts = [20, 30, 40]
        variations = [0.05, 0.1, 0.15]
        seeds = range(42, 47)  # 5 seeds

    print(f"  Press counts: {presses_list}")
    print(f"  Mixes: {mixes}")
    print(f"  Topologies: {topologies}")
    print(f"  Max delays: {max_delays}")
    print(f"  Refractory %: {refractory_pcts}")
    print(f"  Variations: {variations}")
    print(f"  Seeds: {list(seeds)[:3]}...{list(seeds)[-1]} ({len(list(seeds))} total)")
    print()

    # Calculate expected size
    expected_size = (
        len(presses_list) *
        len(mixes) *
        len(topologies) *
        len(max_delays) *
        len(refractory_pcts) *
        len(variations) *
        len(list(seeds))
    )
    print(f"Expected scenarios: {expected_size}")
    print()

    # Generate scenarios
    scenarios = generate_scenario_grid(
        presses_list=presses_list,
        mixes=mixes,
        topologies=topologies,
        max_delays=max_delays,
        refractory_pcts=refractory_pcts,
        variations=variations,
        seeds=list(seeds),
        duration_sec=3600,
        version=args.version
    )

    # Prepare metadata
    metadata = {
        'version': args.version,
        'mode': 'expanded' if args.expanded else 'conservative',
        'parameters': {
            'presses': list(presses_list),
            'mixes': list(mixes),
            'topologies': list(topologies),
            'max_delays': list(max_delays),
            'refractory_pcts': list(refractory_pcts),
            'variations': list(variations),
            'seeds': list(seeds),
            'duration_sec': 3600
        }
    }

    # Save to file
    save_scenario_grid(scenarios, output_path, metadata)

    print()
    print("=" * 70)
    print("SCENARIO GRID COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print(f"  python scripts/generate_training_data.py --scenario-file {args.output}")
    print()


if __name__ == "__main__":
    main()
