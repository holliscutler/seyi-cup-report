"""
Power Profiles Module

Research-validated power consumption profiles for servo presses.
All profiles based on literature research and industry data.
"""

from .profile_base import PowerProfile, PhaseDefinition
from .validated_profiles import (
    VALIDATED_TEMPLATES,
    TEMPLATE_NAMES,
    TEMPLATES_BY_SIZE,
    TEMPLATES_BY_MOTION,
)
from .profile_generator import (
    create_power_profile,
    create_press_fleet,
    get_profile_info,
    list_available_templates,
    validate_profile,
)

__all__ = [
    # Classes
    'PowerProfile',
    'PhaseDefinition',

    # Templates
    'VALIDATED_TEMPLATES',
    'TEMPLATE_NAMES',
    'TEMPLATES_BY_SIZE',
    'TEMPLATES_BY_MOTION',

    # Functions
    'create_power_profile',
    'create_press_fleet',
    'get_profile_info',
    'list_available_templates',
    'validate_profile',
]
