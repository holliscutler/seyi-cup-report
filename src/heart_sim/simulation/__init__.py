"""
Simulation Module

Simulation engine, metrics collection, and data output.
"""

from .engine import SimulationEngine
from .metrics import MetricsCollector
from .data_output import (
    format_for_ai_training,
    format_comparison_data,
    save_results_json,
    save_results_csv,
    create_summary_report,
)

__all__ = [
    'SimulationEngine',
    'MetricsCollector',
    'format_for_ai_training',
    'format_comparison_data',
    'save_results_json',
    'save_results_csv',
    'create_summary_report',
]
