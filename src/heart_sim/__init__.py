"""
Heart Sim - Cardiac-Inspired Servo Press Coordination (v2)

Modular, research-validated simulation of cardiac coordination for servo presses.

Quick Start:
    >>> from heart_sim import create_coordinator_auto, SimulationEngine
    >>> coordinator = create_coordinator_auto(n_presses=6, mix='realistic', seed=42)
    >>> engine = SimulationEngine(coordinator)
    >>> results = engine.run(duration_sec=300)
    >>> print(create_summary_report(results))

Modules:
    - power_profiles: Research-based power consumption profiles
    - press: Cardiac press models and configuration
    - coordination: Network topology and coordinator
    - simulation: Simulation engine, metrics, data output
    - cost: Taiwan electricity pricing
    - utils: Constants and utilities
"""

# Version
__version__ = "2.0.0"

# Power Profiles
from .power_profiles import (
    PowerProfile,
    PhaseDefinition,
    create_power_profile,
    create_press_fleet,
    list_available_templates,
    validate_profile,
    TEMPLATE_NAMES,
)

# Press
from .press import (
    PressConfig,
    create_press_config,
    CardiacPress,
    CardiacState,
)

# Coordination
from .coordination import (
    CardiacCoordinator,
    create_coordinator_auto,
    create_coordinator_from_profiles,
    create_coordinator_from_templates,
    create_baseline_coordinator,
    setup_topology,
)

# Simulation
from .simulation import (
    SimulationEngine,
    MetricsCollector,
    format_for_ai_training,
    format_comparison_data,
    save_results_json,
    save_results_csv,
    create_summary_report,
)

# Cost
from .cost import (
    TaiwanCostCalculator,
    calculate_cost_from_simulation,
    compare_baseline_vs_cardiac_costs,
)

# Utils
from .utils import constants

__all__ = [
    # Version
    '__version__',

    # Power Profiles
    'PowerProfile',
    'PhaseDefinition',
    'create_power_profile',
    'create_press_fleet',
    'list_available_templates',
    'validate_profile',
    'TEMPLATE_NAMES',

    # Press
    'PressConfig',
    'create_press_config',
    'CardiacPress',
    'CardiacState',

    # Coordination
    'CardiacCoordinator',
    'create_coordinator_auto',
    'create_coordinator_from_profiles',
    'create_coordinator_from_templates',
    'create_baseline_coordinator',
    'setup_topology',

    # Simulation
    'SimulationEngine',
    'MetricsCollector',
    'format_for_ai_training',
    'format_comparison_data',
    'save_results_json',
    'save_results_csv',
    'create_summary_report',

    # Cost
    'TaiwanCostCalculator',
    'calculate_cost_from_simulation',
    'compare_baseline_vs_cardiac_costs',

    # Utils
    'constants',
]
