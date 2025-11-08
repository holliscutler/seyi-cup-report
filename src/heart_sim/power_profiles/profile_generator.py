"""
Power Profile Generator

Creates PowerProfile objects from validated templates with optional variations.
"""

import numpy as np
from typing import Optional, Dict, List
from .profile_base import PowerProfile, PhaseDefinition
from .validated_profiles import VALIDATED_TEMPLATES, TEMPLATE_NAMES


def create_power_profile(
    template_name: str,
    variation: float = 0.0,
    seed: Optional[int] = None
) -> PowerProfile:
    """
    Create a PowerProfile from a validated template.

    Args:
        template_name: Name of template from VALIDATED_TEMPLATES
        variation: Random variation to apply (0.0 to 0.2 recommended)
                  Applied to: peak_power, cycle_time
        seed: Random seed for reproducibility

    Returns:
        PowerProfile instance

    Example:
        >>> profile = create_power_profile('medium_standard', variation=0.1, seed=42)
        >>> print(profile.peak_power_kw)  # ~180 kW ± 10%
    """
    if template_name not in VALIDATED_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. "
                        f"Valid options: {TEMPLATE_NAMES}")

    template = VALIDATED_TEMPLATES[template_name].copy()

    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)

    # Apply random variation if requested
    if variation > 0:
        # Vary peak power by ±variation
        peak_variation = np.random.uniform(-variation, variation)
        template['peak_power_kw'] *= (1 + peak_variation)

        # Vary cycle time by ±(variation/2) - less variation in timing
        time_variation = np.random.uniform(-variation/2, variation/2)
        template['cycle_time_sec'] *= (1 + time_variation)

    # Extract template data
    press_type = template['press_type']
    capacity_tons = template['capacity_tons']
    cycle_time_sec = template['cycle_time_sec']
    peak_power_kw = template['peak_power_kw']
    motion_type = template['motion_type']
    phase_defs = template['phases']
    metadata = template['metadata']

    # Build phases
    phases = _build_phases_from_template(phase_defs, peak_power_kw, cycle_time_sec)

    # Create PowerProfile
    profile = PowerProfile(
        press_type=press_type,
        capacity_tons=capacity_tons,
        cycle_time_sec=cycle_time_sec,
        peak_power_kw=peak_power_kw,
        phases=phases,
        motion_type=motion_type,
        metadata=metadata
    )

    return profile


def _build_phases_from_template(
    phase_defs: Dict,
    peak_power_kw: float,
    cycle_time_sec: float
) -> List[PhaseDefinition]:
    """
    Build list of PhaseDefinition objects from template phase definitions.

    Args:
        phase_defs: Dictionary of phase definitions from template
        peak_power_kw: Peak power for this profile (kW)
        cycle_time_sec: Total cycle time (seconds)

    Returns:
        List of PhaseDefinition objects
    """
    phases = []
    cumulative_fraction = 0.0

    # Process phases in order
    phase_order = ['approach', 'forming', 'return', 'idle']

    for phase_name in phase_order:
        if phase_name not in phase_defs:
            continue

        phase_def = phase_defs[phase_name]

        # Calculate fractions
        duration_ratio = phase_def['duration_ratio']
        start_fraction = cumulative_fraction
        end_fraction = cumulative_fraction + duration_ratio

        # Calculate power levels
        power_start = phase_def['power_start_ratio'] * peak_power_kw
        power_end = phase_def['power_end_ratio'] * peak_power_kw

        # Peak power for forming phase
        power_peak = None
        if 'power_peak_ratio' in phase_def:
            power_peak = phase_def['power_peak_ratio'] * peak_power_kw

        # Curve type
        curve_type = phase_def.get('curve_type', 'linear')

        # Create PhaseDefinition
        phase = PhaseDefinition(
            name=phase_name,
            start_fraction=start_fraction,
            end_fraction=end_fraction,
            power_start=power_start,
            power_end=power_end,
            power_peak=power_peak,
            curve_type=curve_type
        )

        phases.append(phase)
        cumulative_fraction = end_fraction

    # Verify phases sum to ~1.0
    total_coverage = sum(p.duration_fraction for p in phases)
    if not (0.99 <= total_coverage <= 1.01):
        # Normalize to exactly 1.0
        for phase in phases:
            scale_factor = 1.0 / total_coverage
            phase.start_fraction *= scale_factor
            phase.end_fraction *= scale_factor

    return phases


def create_press_fleet(
    n_presses: int = 4,
    mix: str = "varied",
    variation: float = 0.1,
    seed: Optional[int] = None
) -> List[PowerProfile]:
    """
    Generate a fleet of press profiles for simulation.

    Args:
        n_presses: Number of presses to generate (4-8 typical)
        mix: Fleet composition strategy:
            - "uniform": All same template
            - "varied": Mix of different templates
            - "realistic": Weighted toward medium presses (most common)
            - "small": Mostly small presses
            - "large": Mostly large presses
        variation: Random variation factor (0.0 to 0.2 recommended)
        seed: Random seed for reproducibility

    Returns:
        List of PowerProfile instances

    Example:
        >>> fleet = create_press_fleet(n_presses=6, mix='realistic', variation=0.1, seed=42)
        >>> for profile in fleet:
        ...     print(profile.press_type, profile.peak_power_kw)
    """
    if seed is not None:
        np.random.seed(seed)

    fleet = []

    if mix == "uniform":
        # All presses use the same template
        template = 'medium_standard'
        for i in range(n_presses):
            profile = create_power_profile(template, variation, seed=seed+i if seed else None)
            fleet.append(profile)

    elif mix == "varied":
        # Cycle through different templates
        templates = [
            'small_fast',
            'medium_standard',
            'medium_coining',
            'large_slow',
            'medium_pulsating',
            'small_high_speed',
            'medium_heavy_gauge',
            'large_progressive',
        ]
        for i in range(n_presses):
            template = templates[i % len(templates)]
            profile = create_power_profile(template, variation, seed=seed+i if seed else None)
            fleet.append(profile)

    elif mix == "realistic":
        # Weighted toward medium presses (most common in factories)
        # Based on research: medium presses dominate industrial installations
        templates = [
            'medium_standard',      # 40% probability
            'medium_standard',
            'medium_coining',       # 15%
            'large_slow',           # 20%
            'small_fast',           # 15%
            'medium_pulsating',     # 10%
        ]

        for i in range(n_presses):
            template = np.random.choice(templates)
            profile = create_power_profile(template, variation, seed=seed+i if seed else None)
            fleet.append(profile)

    elif mix == "small":
        # Mostly small presses
        templates = ['small_fast', 'small_high_speed']
        for i in range(n_presses):
            template = templates[i % len(templates)]
            profile = create_power_profile(template, variation, seed=seed+i if seed else None)
            fleet.append(profile)

    elif mix == "large":
        # Mostly large presses
        templates = ['large_slow', 'large_progressive']
        for i in range(n_presses):
            template = templates[i % len(templates)]
            profile = create_power_profile(template, variation, seed=seed+i if seed else None)
            fleet.append(profile)

    else:
        raise ValueError(f"Unknown mix strategy: {mix}")

    return fleet


def get_profile_info(template_name: str) -> Dict:
    """
    Get information about a profile template without creating it.

    Args:
        template_name: Name of template

    Returns:
        Dictionary with template information
    """
    if template_name not in VALIDATED_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")

    template = VALIDATED_TEMPLATES[template_name]

    return {
        'name': template_name,
        'press_type': template['press_type'],
        'capacity_tons': template['capacity_tons'],
        'peak_power_kw': template['peak_power_kw'],
        'cycle_time_sec': template['cycle_time_sec'],
        'motion_type': template['motion_type'],
        'description': template['metadata'].get('description', ''),
        'applications': template['metadata'].get('applications', ''),
        'energy_per_cycle_kwh': template['metadata'].get('energy_per_cycle_kwh', 0),
    }


def list_available_templates() -> List[str]:
    """Get list of all available template names."""
    return TEMPLATE_NAMES


def validate_profile(profile: PowerProfile) -> Dict[str, bool]:
    """
    Validate that a power profile meets research-based criteria.

    Args:
        profile: PowerProfile to validate

    Returns:
        Dictionary of validation results
    """
    results = {}

    # Check peak power reasonable for capacity
    # Rule of thumb: ~0.9 kW per ton
    expected_peak = profile.capacity_tons * 0.9
    peak_ratio = profile.peak_power_kw / expected_peak
    results['peak_power_reasonable'] = 0.7 <= peak_ratio <= 1.3

    # Check phase coverage
    total_phase_coverage = sum(p.duration_fraction for p in profile.phases)
    results['phases_sum_to_one'] = 0.99 <= total_phase_coverage <= 1.01

    # Check has forming phase
    has_forming = any(p.name == 'forming' for p in profile.phases)
    results['has_forming_phase'] = has_forming

    # Check average power is less than peak
    results['avg_less_than_peak'] = profile.avg_power_kw < profile.peak_power_kw

    # Check energy per cycle is reasonable
    # Rough check: should be in range for given capacity
    min_energy = profile.capacity_tons * 0.002  # kWh
    max_energy = profile.capacity_tons * 0.010  # kWh
    results['energy_in_range'] = min_energy <= profile.energy_per_cycle_kwh <= max_energy

    results['all_valid'] = all(results.values())

    return results
