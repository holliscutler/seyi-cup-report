"""
Test Framework for Cardiac Coordination

Modular testing framework for systematic scenario testing and analysis.

Main Components:
- scenarios: ScenarioConfig and factory functions
- runner: Simulation execution
- analyzers: Power, coordination, cost analysis
- comparators: Comparison and aggregation
- reporters: Report generation (JSON, CSV, Markdown)

Example Usage:
    >>> from test_framework import create_scenario_grid, run_batch, aggregate_across_seeds
    >>> scenarios = create_scenario_grid([4, 5, 6], range(42, 52))
    >>> results = run_batch(scenarios, parallel=True)
    >>> summary = aggregate_across_seeds(results)
"""

# Scenarios
from .scenarios import (
    ScenarioConfig,
    create_single_scenario,
    create_seed_sweep,
    create_press_count_sweep,
    create_scenario_grid,
    create_topology_comparison,
    create_delay_sweep,
    create_mix_comparison,
)

# Runner
from .runner import (
    ScenarioResult,
    run_scenario,
    run_batch,
    save_results,
    load_results,
    filter_results,
)

# Analyzers
from .analyzers import (
    analyze_power_distribution,
    analyze_coordination_behavior,
    analyze_cost_savings,
    analyze_stability,
    analyze_energy_efficiency,
    analyze_all,
)

# Comparators
from .comparators import (
    compare_single_scenario,
    aggregate_across_seeds,
    compare_across_press_counts,
    compare_across_topologies,
    compare_across_mixes,
    find_best_and_worst,
    calculate_summary_statistics,
)

# Reporters
from .reporters import (
    generate_json_report,
    generate_csv_summary,
    generate_markdown_report,
    generate_summary_table,
)


__all__ = [
    # Scenarios
    'ScenarioConfig',
    'create_single_scenario',
    'create_seed_sweep',
    'create_press_count_sweep',
    'create_scenario_grid',
    'create_topology_comparison',
    'create_delay_sweep',
    'create_mix_comparison',
    # Runner
    'ScenarioResult',
    'run_scenario',
    'run_batch',
    'save_results',
    'load_results',
    'filter_results',
    # Analyzers
    'analyze_power_distribution',
    'analyze_coordination_behavior',
    'analyze_cost_savings',
    'analyze_stability',
    'analyze_energy_efficiency',
    'analyze_all',
    # Comparators
    'compare_single_scenario',
    'aggregate_across_seeds',
    'compare_across_press_counts',
    'compare_across_topologies',
    'compare_across_mixes',
    'find_best_and_worst',
    'calculate_summary_statistics',
    # Reporters
    'generate_json_report',
    'generate_csv_summary',
    'generate_markdown_report',
    'generate_summary_table',
]
