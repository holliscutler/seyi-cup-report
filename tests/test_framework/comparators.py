"""
Comparators and Aggregators

Functions for comparing scenarios and aggregating results across multiple runs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
from typing import List, Dict
from src.heart_sim import MetricsCollector

from .runner import ScenarioResult
from .analyzers import (
    analyze_power_distribution,
    analyze_coordination_behavior,
    analyze_cost_savings,
    analyze_energy_efficiency
)


def compare_single_scenario(result: ScenarioResult) -> Dict:
    """
    Compare baseline vs cardiac for a single scenario.

    Args:
        result: ScenarioResult with both baseline and cardiac

    Returns:
        Dictionary with comparison metrics
    """
    # Use MetricsCollector for standard comparison
    comparison = MetricsCollector.compare_baseline_vs_cardiac(
        result.baseline_results,
        result.cardiac_results
    )

    # Additional analysis
    baseline_power = analyze_power_distribution(result.baseline_results)
    cardiac_power = analyze_power_distribution(result.cardiac_results)
    coordination = analyze_coordination_behavior(result.cardiac_results)
    cost_analysis = analyze_cost_savings(result.baseline_results, result.cardiac_results)

    return {
        'config': result.config.to_dict(),
        'comparison': {
            'baseline_peak_kw': comparison['baseline_peak_kw'],
            'cardiac_peak_kw': comparison['cardiac_peak_kw'],
            'peak_reduction_kw': comparison['peak_reduction_kw'],
            'peak_reduction_pct': comparison['peak_reduction_pct'],
            'energy_change_kwh': comparison['energy_change_kwh'],
            'cardiac_wins': comparison['cardiac_peak_kw'] < comparison['baseline_peak_kw'],
        },
        'power_distribution': {
            'baseline_spikes': baseline_power['num_spikes'],
            'cardiac_spikes': cardiac_power['num_spikes'],
            'baseline_cv': baseline_power['cv'],
            'cardiac_cv': cardiac_power['cv'],
        },
        'coordination': {
            'total_delays': coordination['total_delays'],
            'total_collisions_avoided': coordination['total_collisions_avoided'],
            'avg_delay_rate': coordination['avg_delay_rate'],
            'phase_spread_score': coordination['phase_spread_score'],
        },
        'cost_savings': {
            'monthly_savings_ntd': cost_analysis['monthly_savings_ntd'],
            'annual_savings_ntd': cost_analysis['annual_savings_ntd'],
            'annual_savings_usd': cost_analysis['annual_savings_usd'],
        }
    }


def aggregate_across_seeds(results: List[ScenarioResult]) -> Dict:
    """
    Aggregate statistics across multiple seeds.

    All results should have same config except seed.

    Args:
        results: List of ScenarioResults with different seeds

    Returns:
        Dictionary with aggregated statistics
    """
    if not results:
        return {}

    # Get all comparisons
    comparisons = [compare_single_scenario(r) for r in results]

    # Extract metrics
    peak_reductions_pct = [c['comparison']['peak_reduction_pct'] for c in comparisons]
    peak_reductions_kw = [c['comparison']['peak_reduction_kw'] for c in comparisons]
    cardiac_wins = [c['comparison']['cardiac_wins'] for c in comparisons]
    baseline_peaks = [c['comparison']['baseline_peak_kw'] for c in comparisons]
    cardiac_peaks = [c['comparison']['cardiac_peak_kw'] for c in comparisons]
    monthly_savings = [c['cost_savings']['monthly_savings_ntd'] for c in comparisons]
    annual_savings_usd = [c['cost_savings']['annual_savings_usd'] for c in comparisons]

    # Coordination metrics
    total_delays = [c['coordination']['total_delays'] for c in comparisons]
    collisions_avoided = [c['coordination']['total_collisions_avoided'] for c in comparisons]
    phase_spread_scores = [c['coordination']['phase_spread_score'] for c in comparisons]

    # Calculate statistics
    return {
        'n_scenarios': len(results),
        'seeds': [r.config.seed for r in results],
        'config': results[0].config.to_dict(),  # Representative config
        'peak_reduction': {
            'mean_pct': float(np.mean(peak_reductions_pct)),
            'std_pct': float(np.std(peak_reductions_pct)),
            'min_pct': float(np.min(peak_reductions_pct)),
            'max_pct': float(np.max(peak_reductions_pct)),
            'median_pct': float(np.median(peak_reductions_pct)),
            'mean_kw': float(np.mean(peak_reductions_kw)),
        },
        'baseline_peak': {
            'mean_kw': float(np.mean(baseline_peaks)),
            'std_kw': float(np.std(baseline_peaks)),
            'min_kw': float(np.min(baseline_peaks)),
            'max_kw': float(np.max(baseline_peaks)),
        },
        'cardiac_peak': {
            'mean_kw': float(np.mean(cardiac_peaks)),
            'std_kw': float(np.std(cardiac_peaks)),
            'min_kw': float(np.min(cardiac_peaks)),
            'max_kw': float(np.max(cardiac_peaks)),
        },
        'win_rate': float(sum(cardiac_wins) / len(cardiac_wins) * 100),
        'cost_savings': {
            'mean_monthly_ntd': float(np.mean(monthly_savings)),
            'mean_annual_usd': float(np.mean(annual_savings_usd)),
            'total_annual_usd': float(np.sum(annual_savings_usd) / len(annual_savings_usd)),  # Average across seeds
        },
        'coordination': {
            'mean_delays': float(np.mean(total_delays)),
            'mean_collisions_avoided': float(np.mean(collisions_avoided)),
            'mean_phase_spread': float(np.mean(phase_spread_scores)),
        }
    }


def compare_across_press_counts(results: List[ScenarioResult]) -> Dict:
    """
    Compare algorithm performance across different press counts.

    Args:
        results: List of ScenarioResults with varying n_presses

    Returns:
        Dictionary with scaling analysis
    """
    # Group by press count
    by_press_count = {}
    for result in results:
        n = result.config.n_presses
        if n not in by_press_count:
            by_press_count[n] = []
        by_press_count[n].append(result)

    # Aggregate for each press count
    scaling_data = {}
    for n_presses, press_results in sorted(by_press_count.items()):
        scaling_data[n_presses] = aggregate_across_seeds(press_results)

    return {
        'by_press_count': scaling_data,
        'summary': {
            'press_counts': sorted(by_press_count.keys()),
            'total_scenarios': len(results),
        }
    }


def compare_across_topologies(results: List[ScenarioResult]) -> Dict:
    """
    Compare algorithm performance across different topologies.

    Args:
        results: List of ScenarioResults with varying topologies

    Returns:
        Dictionary with topology comparison
    """
    # Group by topology
    by_topology = {}
    for result in results:
        top = result.config.topology
        if top not in by_topology:
            by_topology[top] = []
        by_topology[top].append(result)

    # Aggregate for each topology
    topology_data = {}
    for topology, top_results in by_topology.items():
        topology_data[topology] = aggregate_across_seeds(top_results)

    return {
        'by_topology': topology_data,
        'summary': {
            'topologies': list(by_topology.keys()),
            'total_scenarios': len(results),
        }
    }


def compare_across_mixes(results: List[ScenarioResult]) -> Dict:
    """
    Compare algorithm performance across different fleet mixes.

    Args:
        results: List of ScenarioResults with varying mixes

    Returns:
        Dictionary with mix comparison
    """
    # Group by mix
    by_mix = {}
    for result in results:
        mix = result.config.mix
        if mix not in by_mix:
            by_mix[mix] = []
        by_mix[mix].append(result)

    # Aggregate for each mix
    mix_data = {}
    for mix, mix_results in by_mix.items():
        mix_data[mix] = aggregate_across_seeds(mix_results)

    return {
        'by_mix': mix_data,
        'summary': {
            'mixes': list(by_mix.keys()),
            'total_scenarios': len(results),
        }
    }


def find_best_and_worst(results: List[ScenarioResult]) -> Dict:
    """
    Find best and worst performing scenarios.

    Args:
        results: List of ScenarioResults

    Returns:
        Dictionary with best/worst scenarios
    """
    comparisons = [(r, compare_single_scenario(r)) for r in results]

    # Sort by peak reduction percentage
    sorted_by_reduction = sorted(
        comparisons,
        key=lambda x: x[1]['comparison']['peak_reduction_pct'],
        reverse=True
    )

    best = sorted_by_reduction[0]
    worst = sorted_by_reduction[-1]

    return {
        'best': {
            'config': best[0].config.to_dict(),
            'peak_reduction_pct': best[1]['comparison']['peak_reduction_pct'],
            'peak_reduction_kw': best[1]['comparison']['peak_reduction_kw'],
            'cost_savings_usd': best[1]['cost_savings']['annual_savings_usd'],
        },
        'worst': {
            'config': worst[0].config.to_dict(),
            'peak_reduction_pct': worst[1]['comparison']['peak_reduction_pct'],
            'peak_reduction_kw': worst[1]['comparison']['peak_reduction_kw'],
            'cost_savings_usd': worst[1]['cost_savings']['annual_savings_usd'],
        }
    }


def calculate_summary_statistics(results: List[ScenarioResult]) -> Dict:
    """
    Calculate overall summary statistics across all scenarios.

    Args:
        results: List of ScenarioResults

    Returns:
        Dictionary with summary statistics
    """
    comparisons = [compare_single_scenario(r) for r in results]

    peak_reductions = [c['comparison']['peak_reduction_pct'] for c in comparisons]
    wins = [c['comparison']['cardiac_wins'] for c in comparisons]
    savings_usd = [c['cost_savings']['annual_savings_usd'] for c in comparisons]

    return {
        'total_scenarios': len(results),
        'overall_win_rate_pct': float(sum(wins) / len(wins) * 100),
        'peak_reduction': {
            'mean_pct': float(np.mean(peak_reductions)),
            'std_pct': float(np.std(peak_reductions)),
            'min_pct': float(np.min(peak_reductions)),
            'max_pct': float(np.max(peak_reductions)),
            'median_pct': float(np.median(peak_reductions)),
        },
        'annual_savings_usd': {
            'mean': float(np.mean(savings_usd)),
            'total': float(np.sum(savings_usd)),
            'min': float(np.min(savings_usd)),
            'max': float(np.max(savings_usd)),
        }
    }
