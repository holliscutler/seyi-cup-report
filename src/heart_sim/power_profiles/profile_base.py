"""
PowerProfile Base Class

Represents a realistic servo press power consumption profile over one complete cycle.
Based on research from QUICK_REFERENCE.md and DAY1_RESEARCH_SUMMARY.md.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PhaseDefinition:
    """
    Definition of a single phase in the press cycle.

    Attributes:
        name: Phase name (approach, forming, return, idle)
        start_fraction: Where this phase starts (0-1)
        end_fraction: Where this phase ends (0-1)
        power_start: Power at start of phase (kW)
        power_end: Power at end of phase (kW)
        power_peak: Peak power during phase (kW), if applicable
        curve_type: How power transitions ('linear', 'ramp', 'constant', 'bell')
    """
    name: str
    start_fraction: float
    end_fraction: float
    power_start: float
    power_end: float
    power_peak: Optional[float] = None
    curve_type: str = 'linear'

    @property
    def duration_fraction(self) -> float:
        """Duration of this phase as fraction of total cycle."""
        return self.end_fraction - self.start_fraction

    def get_power_at_fraction(self, cycle_fraction: float) -> float:
        """
        Calculate power at a specific point in this phase.

        Args:
            cycle_fraction: Position in cycle (0-1)

        Returns:
            Power in kW
        """
        if not (self.start_fraction <= cycle_fraction <= self.end_fraction):
            raise ValueError(f"Fraction {cycle_fraction} not in phase {self.name}")

        # Normalize to phase progress (0-1)
        phase_progress = (cycle_fraction - self.start_fraction) / self.duration_fraction

        if self.curve_type == 'constant':
            return self.power_start

        elif self.curve_type == 'linear':
            # Linear interpolation
            return self.power_start + (self.power_end - self.power_start) * phase_progress

        elif self.curve_type == 'ramp':
            # Smooth ramp (ease-in-out)
            smoothed = 0.5 - 0.5 * np.cos(np.pi * phase_progress)
            return self.power_start + (self.power_end - self.power_start) * smoothed

        elif self.curve_type == 'bell':
            # Bell curve (for forming phase)
            # Use sine wave for smooth peak
            if self.power_peak is None:
                self.power_peak = max(self.power_start, self.power_end)

            # Sine from 0 to π gives bell shape
            bell_value = np.sin(np.pi * phase_progress)
            return self.power_start + (self.power_peak - self.power_start) * bell_value

        else:
            # Default to linear
            return self.power_start + (self.power_end - self.power_start) * phase_progress


class PowerProfile:
    """
    Complete power consumption profile for one servo press cycle.

    This class represents the realistic power draw over time for a single
    complete press cycle, including all phases (approach, forming, return, idle).

    Attributes:
        press_type: Type identifier (e.g., 'SMALL_100T', 'MEDIUM_200T')
        capacity_tons: Press capacity in tons
        cycle_time_sec: Total cycle duration in seconds
        peak_power_kw: Maximum power consumption in kW
        phases: List of PhaseDefinition objects
        motion_type: Type of motion profile ('STANDARD', 'COINING', 'PULSATING')
        metadata: Additional information about this profile
    """

    def __init__(
        self,
        press_type: str,
        capacity_tons: float,
        cycle_time_sec: float,
        peak_power_kw: float,
        phases: list[PhaseDefinition],
        motion_type: str = 'STANDARD',
        metadata: Optional[Dict] = None
    ):
        """
        Initialize a power profile.

        Args:
            press_type: Press type identifier
            capacity_tons: Press capacity (tons)
            cycle_time_sec: Cycle duration (seconds)
            peak_power_kw: Peak power consumption (kW)
            phases: List of phase definitions
            motion_type: Motion profile type
            metadata: Additional metadata
        """
        self.press_type = press_type
        self.capacity_tons = capacity_tons
        self.cycle_time_sec = cycle_time_sec
        self.peak_power_kw = peak_power_kw
        self.phases = phases
        self.motion_type = motion_type
        self.metadata = metadata or {}

        # Validate phases
        self._validate_phases()

        # Calculate derived properties
        self._avg_power_kw = None
        self._energy_per_cycle_kwh = None

    def _validate_phases(self):
        """Validate that phases are properly defined."""
        if not self.phases:
            raise ValueError("PowerProfile must have at least one phase")

        # Check that phases cover full cycle (0 to 1)
        total_coverage = sum(p.duration_fraction for p in self.phases)
        if not (0.99 <= total_coverage <= 1.01):
            raise ValueError(f"Phases must cover full cycle, got {total_coverage}")

        # Check ordering
        for i in range(len(self.phases) - 1):
            if self.phases[i].end_fraction > self.phases[i + 1].start_fraction:
                raise ValueError(f"Phases overlap: {self.phases[i].name} and {self.phases[i + 1].name}")

    def get_power_at_time(self, time_sec: float) -> float:
        """
        Get power consumption at a specific time in the cycle.

        Args:
            time_sec: Time since start of cycle (seconds)

        Returns:
            Power consumption in kW
        """
        # Normalize time to cycle fraction
        cycle_fraction = (time_sec % self.cycle_time_sec) / self.cycle_time_sec

        return self.get_power_at_fraction(cycle_fraction)

    def get_power_at_fraction(self, cycle_fraction: float) -> float:
        """
        Get power consumption at a specific fraction of the cycle.

        Args:
            cycle_fraction: Position in cycle (0-1)

        Returns:
            Power consumption in kW
        """
        # Normalize to 0-1 range
        cycle_fraction = cycle_fraction % 1.0

        # Find which phase we're in
        for phase in self.phases:
            if phase.start_fraction <= cycle_fraction <= phase.end_fraction:
                return phase.get_power_at_fraction(cycle_fraction)

        # If we get here, we're in a gap (shouldn't happen with valid phases)
        # Return minimum power
        return min(p.power_start for p in self.phases)

    def get_phase_at_fraction(self, cycle_fraction: float) -> str:
        """
        Get the phase name at a specific fraction of the cycle.

        Args:
            cycle_fraction: Position in cycle (0-1)

        Returns:
            Phase name (e.g., 'approach', 'forming')
        """
        cycle_fraction = cycle_fraction % 1.0

        for phase in self.phases:
            if phase.start_fraction <= cycle_fraction <= phase.end_fraction:
                return phase.name

        return 'unknown'

    def generate_timeseries(self, num_points: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate time-series data for this profile.

        Args:
            num_points: Number of data points to generate

        Returns:
            Tuple of (time_array, power_array, phase_labels)
        """
        time_array = np.linspace(0, self.cycle_time_sec, num_points)
        power_array = np.array([self.get_power_at_time(t) for t in time_array])
        phase_labels = np.array([self.get_phase_at_fraction(t / self.cycle_time_sec)
                                for t in time_array])

        return time_array, power_array, phase_labels

    @property
    def avg_power_kw(self) -> float:
        """Calculate average power over one cycle."""
        if self._avg_power_kw is None:
            # Sample at high resolution for accurate average
            _, power_array, _ = self.generate_timeseries(num_points=500)
            self._avg_power_kw = float(np.mean(power_array))

        return self._avg_power_kw

    @property
    def energy_per_cycle_kwh(self) -> float:
        """Calculate energy consumption per cycle in kWh."""
        if self._energy_per_cycle_kwh is None:
            # Integrate power over time
            time_array, power_array, _ = self.generate_timeseries(num_points=500)
            # Trapezoid integration, convert from kW·s to kWh
            energy_kwh = np.trapz(power_array, time_array) / 3600.0
            self._energy_per_cycle_kwh = float(energy_kwh)

        return self._energy_per_cycle_kwh

    def get_forming_phase_bounds(self) -> Tuple[float, float]:
        """
        Get the start and end fractions of the forming phase.

        Returns:
            Tuple of (start_fraction, end_fraction)
        """
        for phase in self.phases:
            if phase.name == 'forming':
                return (phase.start_fraction, phase.end_fraction)

        # If no explicit forming phase, estimate based on peak power
        # Find where power is above 80% of peak
        high_power_fractions = []
        for i in np.linspace(0, 1, 100):
            if self.get_power_at_fraction(i) > 0.8 * self.peak_power_kw:
                high_power_fractions.append(i)

        if high_power_fractions:
            return (min(high_power_fractions), max(high_power_fractions))
        else:
            # Default to middle third
            return (0.33, 0.66)

    def __repr__(self) -> str:
        return (f"PowerProfile(type={self.press_type}, "
                f"capacity={self.capacity_tons}T, "
                f"cycle={self.cycle_time_sec}s, "
                f"peak={self.peak_power_kw}kW, "
                f"avg={self.avg_power_kw:.1f}kW)")
