"""
Cardiac Press Model

Servo press with cardiac-inspired coordination logic.
Based on heart chamber coordination principles from research/heart/README.md
"""

import numpy as np
from typing import Optional, List, Tuple, Dict
from enum import Enum
from .press_config import PressConfig


class CardiacState(Enum):
    """
    Cardiac states for the press cycle.

    States map to heart chamber phases:
    - IDLE: Diastole rest (chamber filling)
    - APPROACH: Pre-systolic preparation
    - FORMING: Systole (contraction/peak power)
    - RETURN: Early diastole (relaxation)
    - REFRACTORY: Mandatory recovery period
    - DELAYING: Coordination delay (avoid collision)
    """
    IDLE = "IDLE"
    APPROACH = "APPROACH"
    FORMING = "FORMING"
    RETURN = "RETURN"
    REFRACTORY = "REFRACTORY"
    DELAYING = "DELAYING"


class CardiacPress:
    """
    Servo press modeled as a cardiac chamber.

    Key Cardiac Principles (from research):
    1. Complete cycles at constant speed (like heart contractions)
    2. Adjust REST periods between cycles (like variable RR intervals)
    3. Enforce refractory periods (cardiac muscle recovery)
    4. Predict collisions and delay next cycle
    5. Entrainment to natural rhythms (pacemaker hierarchy)

    The press MUST complete its forming operation once started (cannot
    stop mid-stamp), but can adjust the gap before the next cycle.
    """

    def __init__(self, config: PressConfig):
        """
        Initialize a cardiac press.

        Args:
            config: PressConfig with all press parameters
        """
        self.config = config
        self.power_profile = config.power_profile

        # Identity
        self.press_id = config.press_id
        self.cycle_time = config.cycle_time_sec
        self.natural_frequency = 1.0 / self.cycle_time

        # Cardiac parameters
        self.min_refractory = config.min_refractory_sec
        self.max_delay = config.max_delay_sec
        self.prediction_window = config.prediction_window_sec

        # Phase tracking (0-1, where 0=start of cycle, 1=end of cycle)
        if config.initial_phase is not None:
            self.phase = config.initial_phase
        else:
            self.phase = np.random.uniform(0.0, 1.0)

        self.prev_phase = self.phase
        self.position = self.phase * self.cycle_time  # Absolute time position

        # Cardiac state machine
        self.state = CardiacState.IDLE
        self.refractory_timer = 0.0     # Current refractory countdown
        self.additional_delay = 0.0     # Extra delay added this cycle
        self.is_delaying = False        # Currently in added delay period

        # Entrainment tracking
        self.is_pacemaker = config.is_pacemaker
        self.pacemaker_ref: Optional['CardiacPress'] = None

        # Neighbors for local sensing (network topology)
        self.neighbors: List['CardiacPress'] = []

        # Statistics
        self.cycle_count = 0
        self.delay_count = 0
        self.collision_avoided = 0
        self.total_delay_added = 0.0

        # Get forming phase bounds from power profile
        self.forming_start, self.forming_end = self.power_profile.get_forming_phase_bounds()

    def add_neighbor(self, neighbor: 'CardiacPress'):
        """
        Add a neighbor press for coordination.

        Args:
            neighbor: Another CardiacPress instance
        """
        if neighbor not in self.neighbors and neighbor.press_id != self.press_id:
            self.neighbors.append(neighbor)

    def set_pacemaker(self, is_pacemaker: bool, pacemaker_ref: Optional['CardiacPress'] = None):
        """
        Set entrainment hierarchy.

        Args:
            is_pacemaker: True if this is the fastest press (sets rhythm)
            pacemaker_ref: Reference to the pacemaker press (if not pacemaker)
        """
        self.is_pacemaker = is_pacemaker
        self.pacemaker_ref = pacemaker_ref

    def get_power_kw(self) -> float:
        """
        Get current power consumption from power profile.

        Returns:
            Current power consumption in kW
        """
        return self.power_profile.get_power_at_fraction(self.phase)

    def get_current_phase_name(self) -> str:
        """
        Get the name of the current phase.

        Returns:
            Phase name (e.g., 'approach', 'forming', 'return', 'idle')
        """
        return self.power_profile.get_phase_at_fraction(self.phase)

    def update_state(self):
        """Update cardiac state based on current phase and timers."""
        phase = self.phase % 1.0

        # Check if in forming phase (high-power operation)
        if self.forming_start <= phase <= self.forming_end:
            self.state = CardiacState.FORMING

        # Check if in approach (before forming)
        elif phase < self.forming_start:
            self.state = CardiacState.APPROACH

        # Check if in return (after forming, before idle)
        elif self.forming_end < phase < 0.85:  # Typical return ends around 85%
            self.state = CardiacState.RETURN

        # Check if in idle/rest period
        else:
            # Priority: refractory > delaying > idle
            if self.refractory_timer > 0:
                self.state = CardiacState.REFRACTORY
            elif self.is_delaying:
                self.state = CardiacState.DELAYING
            else:
                self.state = CardiacState.IDLE

    def in_forming_phase(self) -> bool:
        """Check if currently in forming phase (must complete)."""
        return self.forming_start <= (self.phase % 1.0) <= self.forming_end

    def just_entered_forming(self) -> bool:
        """Detect if just entered forming phase (cardiac contraction start)."""
        return (self.prev_phase < self.forming_start and
                self.phase >= self.forming_start)

    def can_add_delay(self) -> bool:
        """
        Check if we can add delay to avoid collision.

        Can only add delay when:
        - In idle phase (not during critical operations)
        - Not currently in refractory period
        - Not already delaying
        """
        phase = self.phase % 1.0
        # Can delay in late return or idle phase (after 85% of cycle)
        return (phase >= 0.85 and
                self.refractory_timer <= 0 and
                not self.is_delaying)

    def predict_neighbor_peaks(self) -> List[Tuple[str, float]]:
        """
        Predict when neighbors will enter forming phase.

        Returns:
            List of (neighbor_id, time_to_forming) tuples within prediction window
        """
        predictions = []

        for neighbor in self.neighbors:
            # Calculate neighbor's time to forming phase
            neighbor_phase = neighbor.phase % 1.0
            neighbor_forming_start = neighbor.forming_start

            if neighbor_phase < neighbor_forming_start:
                # Neighbor hasn't reached forming yet in current cycle
                time_to_forming = (neighbor_forming_start - neighbor_phase) * neighbor.cycle_time
            else:
                # Neighbor past forming, predict next cycle
                time_to_forming = ((1.0 - neighbor_phase) + neighbor_forming_start) * neighbor.cycle_time

            # Only include if within prediction window
            if time_to_forming <= self.prediction_window:
                predictions.append((neighbor.press_id, time_to_forming))

        return predictions

    def calculate_collision_risk(self) -> Tuple[float, bool]:
        """
        Calculate collision risk with neighbors.

        Collision = simultaneous forming phases (high power overlap)

        Returns:
            (risk_score, should_delay): Risk score [0-1] and whether to delay
        """
        if self.is_pacemaker:
            # Pacemakers don't delay (they set the rhythm)
            return 0.0, False

        # Only consider delaying if in delay window
        if not self.can_add_delay():
            return 0.0, False

        # Predict when we would enter forming if we continue now
        current_phase = self.phase % 1.0

        # Time until we would enter forming (completing current cycle)
        if current_phase < self.forming_start:
            # We'll enter forming in this cycle
            time_to_my_forming = (self.forming_start - current_phase) * self.cycle_time
        else:
            # We'll enter forming in next cycle
            time_to_my_forming = ((1.0 - current_phase) + self.forming_start) * self.cycle_time

        # Check neighbor predictions
        neighbor_peaks = self.predict_neighbor_peaks()

        if not neighbor_peaks:
            return 0.0, False

        # Calculate overlap risk
        max_risk = 0.0
        collision_detected = False

        # Duration of forming phase
        forming_duration = (self.forming_end - self.forming_start) * self.cycle_time

        for neighbor_id, neighbor_time in neighbor_peaks:
            # Time difference between our forming starts
            time_diff = abs(time_to_my_forming - neighbor_time)

            # Risk increases as forming phases get closer
            if time_diff < forming_duration:
                # Direct overlap risk
                overlap_ratio = 1.0 - (time_diff / forming_duration)
                risk = overlap_ratio ** 2  # Quadratic penalty for close overlaps
                max_risk = max(max_risk, risk)

                if risk > 0.5:  # Significant collision risk
                    collision_detected = True

        return max_risk, collision_detected

    def calculate_optimal_delay(self) -> float:
        """
        Calculate optimal delay to avoid collision.

        Returns:
            delay_seconds: How long to delay (0 if no delay needed)
        """
        risk_score, should_delay = self.calculate_collision_risk()

        if not should_delay:
            return 0.0

        # Get neighbor predictions
        neighbor_peaks = self.predict_neighbor_peaks()

        if not neighbor_peaks:
            return 0.0

        # Find the nearest neighbor peak
        nearest_time = min(time for _, time in neighbor_peaks)

        # Calculate delay to shift our peak past the neighbor's
        # We want to start forming AFTER neighbor's forming phase ends
        forming_duration = (self.forming_end - self.forming_start) * self.cycle_time
        safety_margin = 0.15 * self.cycle_time  # 15% of cycle time buffer

        # Delay enough to miss the overlap window
        optimal_delay = nearest_time + forming_duration + safety_margin

        # Add cardiac variability (HRV-inspired)
        # Slight randomness to prevent perfect synchronization
        variability = np.random.uniform(-0.05, 0.05) * self.cycle_time
        optimal_delay += variability

        # Clamp to maximum allowed delay
        optimal_delay = max(0.0, min(optimal_delay, self.max_delay))

        return optimal_delay

    def step(self, dt: float = 0.5):
        """
        Advance cardiac press by one timestep.

        Key cardiac principle: Complete cycle at constant speed,
        adjust only the rest period between cycles.

        Args:
            dt: Timestep in seconds
        """
        # Store previous phase
        self.prev_phase = self.phase

        # Update refractory timer
        if self.refractory_timer > 0:
            self.refractory_timer -= dt
            if self.refractory_timer <= 0:
                self.is_delaying = False

        # Cardiac coordination logic
        current_phase = self.phase % 1.0

        # Check if we should add delay (only in idle phase)
        if self.can_add_delay() and self.additional_delay == 0:
            # Calculate if delay is needed
            delay_needed = self.calculate_optimal_delay()

            if delay_needed > 0:
                # Enter delay state
                self.additional_delay = delay_needed
                self.is_delaying = True
                self.refractory_timer = delay_needed
                self.delay_count += 1
                self.total_delay_added += delay_needed

                # Don't advance position this step (start of delay)
                self.update_state()
                return

        # If in refractory/delay, don't advance
        if self.refractory_timer > 0:
            self.update_state()
            return

        # Normal advancement at constant 1.0x speed
        self.position += dt

        # Update phase
        self.phase = (self.position % self.cycle_time) / self.cycle_time

        # Detect cycle completion
        if self.prev_phase > 0.60 and self.phase < self.prev_phase:
            # Completed a cycle
            self.cycle_count += 1
            self.additional_delay = 0.0  # Reset delay for next cycle

            # Enter mandatory refractory period after forming
            if self.refractory_timer <= 0:
                self.refractory_timer = self.min_refractory

        # Detect forming entry (contraction start)
        if self.just_entered_forming():
            # Check if we avoided a collision
            neighbor_peaks = self.predict_neighbor_peaks()
            if len(neighbor_peaks) > 0:
                nearest_time = min(time for _, time in neighbor_peaks)
                forming_duration = (self.forming_end - self.forming_start) * self.cycle_time

                if nearest_time > forming_duration:
                    # Successfully avoided collision
                    self.collision_avoided += 1

        # Update state
        self.update_state()

    def get_status(self) -> Dict:
        """
        Get current cardiac status.

        Returns:
            Dictionary with current status information
        """
        risk_score, should_delay = self.calculate_collision_risk()

        return {
            'press_id': self.press_id,
            'phase': self.phase,
            'state': self.state.value,
            'phase_name': self.get_current_phase_name(),
            'power_kw': self.get_power_kw(),
            'is_pacemaker': self.is_pacemaker,
            'refractory_timer': self.refractory_timer,
            'additional_delay': self.additional_delay,
            'is_delaying': self.is_delaying,
            'collision_risk': risk_score,
            'cycle_count': self.cycle_count,
            'delay_count': self.delay_count,
            'collision_avoided': self.collision_avoided,
            'total_delay_added': self.total_delay_added,
        }

    def reset(self):
        """Reset press to initial state (useful for multiple simulation runs)."""
        if self.config.initial_phase is not None:
            self.phase = self.config.initial_phase
        else:
            self.phase = np.random.uniform(0.0, 1.0)

        self.prev_phase = self.phase
        self.position = self.phase * self.cycle_time
        self.state = CardiacState.IDLE
        self.refractory_timer = 0.0
        self.additional_delay = 0.0
        self.is_delaying = False

        # Reset stats
        self.cycle_count = 0
        self.delay_count = 0
        self.collision_avoided = 0
        self.total_delay_added = 0.0

    def __repr__(self) -> str:
        return (f"CardiacPress(id={self.press_id}, "
                f"type={self.power_profile.press_type}, "
                f"cycle={self.cycle_time}s, "
                f"phase={self.phase:.3f}, "
                f"state={self.state.value})")
