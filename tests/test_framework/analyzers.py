"""
Analysis Functions

Provides modular analysis functions for power distribution, coordination behavior,
cost savings, and other important metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from typing import Dict, List
from src.heart_sim import MetricsCollector


def analyze_power_distribution(results: Dict) -> Dict:
    """
    Analyze power distribution characteristics.

    Args:
        results: Simulation results dictionary

    Returns:
        Dictionary with power distribution metrics
    """
    power = np.array(results['history']['aggregate_power'])

    # Basic statistics
    mean_power = float(np.mean(power))
    std_power = float(np.std(power))
    peak_power = float(np.max(power))
    min_power = float(np.min(power))

    # Percentiles
    percentiles = {
        'p50': float(np.percentile(power, 50)),
        'p75': float(np.percentile(power, 75)),
        'p90': float(np.percentile(power, 90)),
        'p95': float(np.percentile(power, 95)),
        'p99': float(np.percentile(power, 99)),
    }

    # Coefficient of variation
    cv = std_power / mean_power if mean_power > 0 else 0

    # Spike analysis (> 2 std dev above mean)
    spike_threshold = mean_power + 2 * std_power
    num_spikes = int(np.sum(power > spike_threshold))
    spike_percentage = float(num_spikes / len(power) * 100)

    # Histogram bins for distribution
    hist, bin_edges = np.histogram(power, bins=20)
    histogram = {
        'counts': hist.tolist(),
        'bin_edges': bin_edges.tolist(),
    }

    return {
        'mean_power_kw': mean_power,
        'std_power_kw': std_power,
        'cv': cv,
        'peak_power_kw': peak_power,
        'min_power_kw': min_power,
        'percentiles': percentiles,
        'spike_threshold_kw': float(spike_threshold),
        'num_spikes': num_spikes,
        'spike_percentage': spike_percentage,
        'histogram': histogram,
    }


def analyze_coordination_behavior(results: Dict) -> Dict:
    """
    Analyze coordination behavior and effectiveness.

    Args:
        results: Simulation results dictionary (cardiac only)

    Returns:
        Dictionary with coordination metrics
    """
    final_stats = results['final_press_stats']

    # Per-press coordination activity
    press_data = []
    for press_id, stats in final_stats.items():
        delay_rate = stats['delay_count'] / stats['cycle_count'] \
            if stats['cycle_count'] > 0 else 0

        press_data.append({
            'press_id': press_id,
            'cycles': stats['cycle_count'],
            'delays': stats['delay_count'],
            'collisions_avoided': stats['collisions_avoided'],
            'total_delay_time_sec': stats['total_delay_added'],
            'delay_rate': delay_rate,
        })

    # Aggregate statistics
    total_cycles = sum(d['cycles'] for d in press_data)
    total_delays = sum(d['delays'] for d in press_data)
    total_collisions_avoided = sum(d['collisions_avoided'] for d in press_data)
    total_delay_time = sum(d['total_delay_time_sec'] for d in press_data)

    avg_delay_rate = np.mean([d['delay_rate'] for d in press_data])
    avg_delay_duration = total_delay_time / total_delays if total_delays > 0 else 0

    # Phase spread analysis
    metrics = MetricsCollector.calculate_all_metrics(results)

    return {
        'total_cycles': total_cycles,
        'total_delays': total_delays,
        'total_collisions_avoided': total_collisions_avoided,
        'total_delay_time_sec': float(total_delay_time),
        'avg_delay_rate': float(avg_delay_rate),
        'avg_delay_duration_sec': float(avg_delay_duration),
        'phase_spread_score': float(metrics['phase_spread_score']),
        'avg_collision_risk': float(metrics['avg_collision_risk']),
        'per_press': press_data,
    }


def analyze_cost_savings(baseline_results: Dict, cardiac_results: Dict) -> Dict:
    """
    Analyze cost savings from cardiac coordination.

    Args:
        baseline_results: Baseline simulation results
        cardiac_results: Cardiac simulation results

    Returns:
        Dictionary with cost analysis
    """
    from src.heart_sim.cost import TaiwanCostCalculator

    # Get metrics
    baseline_metrics = MetricsCollector.calculate_all_metrics(baseline_results)
    cardiac_metrics = MetricsCollector.calculate_all_metrics(cardiac_results)

    # Calculate costs
    cost_calc = TaiwanCostCalculator()

    baseline_cost = cost_calc.calculate_total_cost(
        energy_kwh=baseline_metrics['total_energy_kwh'],
        peak_power_kw=baseline_metrics['peak_power_kw']
    )

    cardiac_cost = cost_calc.calculate_total_cost(
        energy_kwh=cardiac_metrics['total_energy_kwh'],
        peak_power_kw=cardiac_metrics['peak_power_kw']
    )

    # Savings
    energy_savings_ntd = baseline_cost['energy_cost_ntd'] - cardiac_cost['energy_cost_ntd']
    demand_savings_ntd = baseline_cost['monthly_demand_charge_ntd'] - cardiac_cost['monthly_demand_charge_ntd']
    total_savings_ntd = baseline_cost['total_monthly_cost_ntd'] - cardiac_cost['total_monthly_cost_ntd']

    # Annual projections
    annual_savings_ntd = total_savings_ntd * 12
    annual_savings_usd = annual_savings_ntd / 31.0  # Approximate conversion

    return {
        'baseline_cost_ntd': baseline_cost['total_monthly_cost_ntd'],
        'cardiac_cost_ntd': cardiac_cost['total_monthly_cost_ntd'],
        'monthly_savings_ntd': float(total_savings_ntd),
        'annual_savings_ntd': float(annual_savings_ntd),
        'annual_savings_usd': float(annual_savings_usd),
        'energy_savings_ntd': float(energy_savings_ntd),
        'demand_savings_ntd': float(demand_savings_ntd),
        'savings_breakdown': {
            'energy_pct': float(energy_savings_ntd / total_savings_ntd * 100) if total_savings_ntd != 0 else 0,
            'demand_pct': float(demand_savings_ntd / total_savings_ntd * 100) if total_savings_ntd != 0 else 0,
        }
    }


def analyze_stability(results: Dict, window_size: int = 100) -> Dict:
    """
    Analyze temporal stability of power draw.

    Args:
        results: Simulation results dictionary
        window_size: Window size for rolling statistics

    Returns:
        Dictionary with stability metrics
    """
    power = np.array(results['history']['aggregate_power'])

    # Rolling mean and std
    rolling_means = []
    rolling_stds = []

    for i in range(len(power) - window_size):
        window = power[i:i+window_size]
        rolling_means.append(np.mean(window))
        rolling_stds.append(np.std(window))

    rolling_means = np.array(rolling_means)
    rolling_stds = np.array(rolling_stds)

    # Stability metrics
    mean_drift = float(np.std(rolling_means))  # How much the mean drifts
    std_stability = float(np.std(rolling_stds))  # How stable the variability is

    # Oscillation detection (simple autocorrelation at lag=1)
    if len(power) > 1:
        autocorr_lag1 = float(np.corrcoef(power[:-1], power[1:])[0, 1])
    else:
        autocorr_lag1 = 0.0

    return {
        'mean_drift': mean_drift,
        'std_stability': std_stability,
        'autocorr_lag1': autocorr_lag1,
        'rolling_mean_range': {
            'min': float(np.min(rolling_means)) if len(rolling_means) > 0 else 0,
            'max': float(np.max(rolling_means)) if len(rolling_means) > 0 else 0,
        }
    }


def analyze_energy_efficiency(results: Dict) -> Dict:
    """
    Analyze energy efficiency metrics.

    Args:
        results: Simulation results dictionary

    Returns:
        Dictionary with energy efficiency metrics
    """
    metrics = MetricsCollector.calculate_all_metrics(results)
    power = np.array(results['history']['aggregate_power'])

    # Load factor (avg / peak)
    load_factor = float(metrics['avg_power_kw'] / metrics['peak_power_kw']) \
        if metrics['peak_power_kw'] > 0 else 0

    # Peak-to-average ratio
    peak_to_avg_ratio = float(metrics['peak_power_kw'] / metrics['avg_power_kw']) \
        if metrics['avg_power_kw'] > 0 else 0

    # Time spent above various thresholds
    mean_power = float(np.mean(power))
    time_above_mean = float(np.sum(power > mean_power) / len(power) * 100)
    time_above_150pct = float(np.sum(power > mean_power * 1.5) / len(power) * 100)
    time_above_200pct = float(np.sum(power > mean_power * 2.0) / len(power) * 100)

    return {
        'total_energy_kwh': float(metrics['total_energy_kwh']),
        'avg_power_kw': float(metrics['avg_power_kw']),
        'peak_power_kw': float(metrics['peak_power_kw']),
        'load_factor': load_factor,
        'peak_to_avg_ratio': peak_to_avg_ratio,
        'time_above_mean_pct': time_above_mean,
        'time_above_150pct_mean': time_above_150pct,
        'time_above_200pct_mean': time_above_200pct,
    }


def analyze_all(baseline_results: Dict, cardiac_results: Dict) -> Dict:
    """
    Run all analysis functions and return comprehensive report.

    Args:
        baseline_results: Baseline simulation results
        cardiac_results: Cardiac simulation results

    Returns:
        Dictionary with all analysis results
    """
    return {
        'baseline': {
            'power_distribution': analyze_power_distribution(baseline_results),
            'energy_efficiency': analyze_energy_efficiency(baseline_results),
            'stability': analyze_stability(baseline_results),
        },
        'cardiac': {
            'power_distribution': analyze_power_distribution(cardiac_results),
            'coordination_behavior': analyze_coordination_behavior(cardiac_results),
            'energy_efficiency': analyze_energy_efficiency(cardiac_results),
            'stability': analyze_stability(cardiac_results),
        },
        'cost_savings': analyze_cost_savings(baseline_results, cardiac_results),
    }
