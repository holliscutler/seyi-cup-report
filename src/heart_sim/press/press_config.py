"""
Press Configuration

Clean configuration dataclass for servo press setup.
"""

from dataclasses import dataclass, field
from typing import Optional
from ..power_profiles import PowerProfile


@dataclass
class PressConfig:
    """
    Configuration for a single servo press in the cardiac coordination system.

    Attributes:
        press_id: Unique identifier for this press
        power_profile: PowerProfile defining power consumption characteristics
        initial_phase: Starting phase in cycle (0-1), None for random
        min_refractory_sec: Minimum rest after forming (seconds)
        max_delay_sec: Maximum allowable delay (seconds)
        prediction_window_sec: How far ahead to predict collisions (seconds)
        is_pacemaker: Whether this press sets the rhythm (fastest press)
    """

    press_id: str
    power_profile: PowerProfile
    initial_phase: Optional[float] = None
    min_refractory_sec: Optional[float] = None
    max_delay_sec: float = 5.0
    prediction_window_sec: float = 10.0
    is_pacemaker: bool = False

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        # Set min_refractory based on cycle time if not provided
        if self.min_refractory_sec is None:
            # Default: 30% of cycle time (research-based cardiac recovery)
            self.min_refractory_sec = 0.30 * self.power_profile.cycle_time_sec

        # Validate initial_phase
        if self.initial_phase is not None:
            if not (0.0 <= self.initial_phase <= 1.0):
                raise ValueError(f"initial_phase must be in [0, 1], got {self.initial_phase}")

        # Validate max_delay
        if self.max_delay_sec < 0:
            raise ValueError(f"max_delay_sec must be >= 0, got {self.max_delay_sec}")

    @property
    def cycle_time_sec(self) -> float:
        """Get cycle time from power profile."""
        return self.power_profile.cycle_time_sec

    @property
    def peak_power_kw(self) -> float:
        """Get peak power from power profile."""
        return self.power_profile.peak_power_kw

    @property
    def press_type(self) -> str:
        """Get press type from power profile."""
        return self.power_profile.press_type

    @property
    def capacity_tons(self) -> float:
        """Get capacity from power profile."""
        return self.power_profile.capacity_tons

    def get_forming_phase_bounds(self) -> tuple[float, float]:
        """
        Get the start and end fractions of the forming phase.

        Returns:
            Tuple of (start_fraction, end_fraction)
        """
        return self.power_profile.get_forming_phase_bounds()

    def __repr__(self) -> str:
        return (f"PressConfig(id={self.press_id}, "
                f"type={self.press_type}, "
                f"cycle={self.cycle_time_sec}s, "
                f"peak={self.peak_power_kw}kW)")


def create_press_config(
    press_id: str,
    power_profile: PowerProfile,
    initial_phase: Optional[float] = None,
    max_delay_sec: float = 5.0,
    is_pacemaker: bool = False
) -> PressConfig:
    """
    Convenience function to create a PressConfig.

    Args:
        press_id: Unique identifier
        power_profile: PowerProfile for this press
        initial_phase: Starting phase (0-1), None for random
        max_delay_sec: Maximum delay allowed (seconds)
        is_pacemaker: Whether this is the rhythm-setting press

    Returns:
        PressConfig instance
    """
    return PressConfig(
        press_id=press_id,
        power_profile=power_profile,
        initial_phase=initial_phase,
        max_delay_sec=max_delay_sec,
        is_pacemaker=is_pacemaker
    )
