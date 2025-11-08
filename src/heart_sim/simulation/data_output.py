"""
Data Output Formatting

Prepares simulation data for analysis and AI training.
"""

import json
from typing import Dict, Optional
from .metrics import MetricsCollector


def format_for_ai_training(
    results: Dict,
    experiment_name: str = "cardiac_simulation",
    include_timeseries: bool = True
) -> Dict:
    """
    Format simulation results for AI/ML training.

    Args:
        results: Complete simulation results from SimulationEngine
        experiment_name: Name/identifier for this experiment
        include_timeseries: Whether to include full time-series data (can be large)

    Returns:
        Dictionary formatted for AI training with:
        - experiment_metadata
        - timeseries_data (if included)
        - performance_metrics
        - ai_training_features
        - press_individual_stats
    """
    # Calculate metrics
    all_metrics = MetricsCollector.calculate_all_metrics(results)
    ai_features = MetricsCollector.calculate_ai_features(results)

    output = {
        'experiment_metadata': {
            'name': experiment_name,
            'duration_sec': results['metadata']['duration_sec'],
            'num_steps': results['metadata']['num_steps'],
            'num_presses': results['metadata']['num_presses'],
            'topology': results['metadata']['topology'],
            'pacemaker': results['metadata']['pacemaker'],
            'press_configs': results['press_configs'],
        },

        'performance_metrics': all_metrics,

        'ai_training_features': ai_features,

        'press_individual_stats': results['final_press_stats'],
    }

    # Optionally include time-series (can be large)
    if include_timeseries:
        output['timeseries_data'] = results['history']

    return output


def format_comparison_data(
    baseline_results: Dict,
    cardiac_results: Dict,
    experiment_name: str = "baseline_vs_cardiac"
) -> Dict:
    """
    Format comparison between baseline and cardiac results.

    Args:
        baseline_results: Results from baseline simulation
        cardiac_results: Results from cardiac simulation
        experiment_name: Experiment identifier

    Returns:
        Dictionary with comparison data
    """
    comparison = MetricsCollector.compare_baseline_vs_cardiac(
        baseline_results, cardiac_results
    )

    return {
        'experiment_metadata': {
            'name': experiment_name,
            'type': 'comparison',
            'baseline_duration': baseline_results['metadata']['duration_sec'],
            'cardiac_duration': cardiac_results['metadata']['duration_sec'],
        },

        'comparison_metrics': comparison,

        'baseline_metrics': MetricsCollector.calculate_all_metrics(baseline_results),
        'cardiac_metrics': MetricsCollector.calculate_all_metrics(cardiac_results),
    }


def save_results_json(data: Dict, filename: str):
    """
    Save results to JSON file.

    Args:
        data: Data dictionary to save
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def save_results_csv(results: Dict, filename_prefix: str):
    """
    Save time-series results to CSV files.

    Creates multiple CSV files:
    - {prefix}_aggregate_power.csv
    - {prefix}_individual_powers.csv
    - {prefix}_phases.csv
    - {prefix}_states.csv

    Args:
        results: Complete simulation results
        filename_prefix: Prefix for output filenames
    """
    import pandas as pd

    history = results['history']
    time = history['time']

    # Aggregate power
    df_aggregate = pd.DataFrame({
        'time_sec': time,
        'aggregate_power_kw': history['aggregate_power'],
    })
    df_aggregate.to_csv(f"{filename_prefix}_aggregate_power.csv", index=False)

    # Individual powers
    power_data = {'time_sec': time}
    for press_id, powers in history['individual_powers'].items():
        power_data[f'{press_id}_power_kw'] = powers
    df_powers = pd.DataFrame(power_data)
    df_powers.to_csv(f"{filename_prefix}_individual_powers.csv", index=False)

    # Phases
    phase_data = {'time_sec': time}
    for press_id, phases in history['phases'].items():
        phase_data[f'{press_id}_phase'] = phases
    df_phases = pd.DataFrame(phase_data)
    df_phases.to_csv(f"{filename_prefix}_phases.csv", index=False)

    # States
    state_data = {'time_sec': time}
    for press_id, states in history['states'].items():
        state_data[f'{press_id}_state'] = states
    df_states = pd.DataFrame(state_data)
    df_states.to_csv(f"{filename_prefix}_states.csv", index=False)

    print(f"Saved CSV files with prefix: {filename_prefix}")


def create_summary_report(results: Dict, include_cost: bool = False,
                         cost_data: Optional[Dict] = None) -> str:
    """
    Create a human-readable summary report.

    Args:
        results: Complete simulation results
        include_cost: Whether to include cost information
        cost_data: Cost calculation results (if include_cost=True)

    Returns:
        Formatted string report
    """
    metrics = MetricsCollector.calculate_all_metrics(results)
    metadata = results['metadata']

    lines = []
    lines.append("="*70)
    lines.append("CARDIAC COORDINATION SIMULATION SUMMARY")
    lines.append("="*70)

    lines.append(f"\nSimulation Configuration:")
    lines.append(f"  Duration: {metadata['duration_sec']:.1f}s")
    lines.append(f"  Presses: {metadata['num_presses']}")
    lines.append(f"  Topology: {metadata['topology']}")
    lines.append(f"  Pacemaker: {metadata['pacemaker']}")

    lines.append(f"\nPower Metrics:")
    lines.append(f"  Peak Power: {metrics['peak_power_kw']:.1f} kW @ {metrics['peak_time_sec']:.1f}s")
    lines.append(f"  Average Power: {metrics['avg_power_kw']:.1f} kW")
    lines.append(f"  P90/P95/P99: {metrics['p90_power_kw']:.1f} / "
                f"{metrics['p95_power_kw']:.1f} / {metrics['p99_power_kw']:.1f} kW")
    lines.append(f"  Total Energy: {metrics['total_energy_kwh']:.2f} kWh")
    lines.append(f"  Power Std Dev: {metrics['std_power_kw']:.1f} kW "
                f"(CV: {metrics['cv_power']:.2%})")

    lines.append(f"\nCoordination Metrics:")
    lines.append(f"  Total Delays: {metrics['total_delays']}")
    lines.append(f"  Total Cycles: {metrics['total_cycles']}")
    lines.append(f"  Collisions Avoided: {metrics['total_collisions_avoided']}")
    lines.append(f"  Total Delay Time: {metrics['total_delay_time_sec']:.1f}s")
    lines.append(f"  Avg Collision Risk: {metrics['avg_collision_risk']:.2%}")
    lines.append(f"  Phase Spread Score: {metrics['phase_spread_score']:.2%}")
    lines.append(f"  Delay Rate: {metrics['delay_rate']:.2%}")

    if include_cost and cost_data:
        lines.append(f"\nCost Analysis (Taiwan):")
        lines.append(f"  Energy Cost: NT$ {cost_data['energy_cost_ntd']:.0f}")
        lines.append(f"  Demand Charge: NT$ {cost_data['monthly_demand_charge_ntd']:.0f}")
        lines.append(f"  Total Monthly Cost: NT$ {cost_data['total_monthly_cost_ntd']:.0f}")

    lines.append(f"\nPress Individual Stats:")
    for press_id, stats in results['final_press_stats'].items():
        config = results['press_configs'][press_id]
        pm = " [PACEMAKER]" if config['is_pacemaker'] else ""
        lines.append(f"  {press_id}{pm}:")
        lines.append(f"    Type: {config['press_type']}, "
                    f"Capacity: {config['capacity_tons']}T, "
                    f"Cycle: {config['cycle_time_sec']}s")
        lines.append(f"    Cycles: {stats['cycle_count']}, "
                    f"Delays: {stats['delay_count']}, "
                    f"Collisions Avoided: {stats['collisions_avoided']}")
        lines.append(f"    Total Delay Added: {stats['total_delay_added']:.1f}s, "
                    f"Final Phase: {stats['final_phase']:.3f}")

    lines.append("="*70)

    return "\n".join(lines)
