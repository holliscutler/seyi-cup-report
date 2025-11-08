"""
Simulation Engine

Runs cardiac coordination simulations and collects time-series data.
Separated from coordinator for clean architecture.
"""

import numpy as np
from typing import Dict, List, Optional
from ..coordination import CardiacCoordinator
from ..utils.constants import DEFAULT_TIMESTEP_SEC


class SimulationEngine:
    """
    Simulation engine for cardiac press coordination.

    Responsibilities:
    - Run simulation time steps
    - Collect time-series data
    - Track history
    - Prepare data for metrics/AI analysis

    Does NOT:
    - Calculate metrics (see MetricsCollector)
    - Calculate costs (see TaiwanCostCalculator)
    - Visualize (see visualization module)
    """

    def __init__(self, coordinator: CardiacCoordinator):
        """
        Initialize simulation engine.

        Args:
            coordinator: CardiacCoordinator instance
        """
        self.coordinator = coordinator
        self.history = self._initialize_history()
        self.current_time = 0.0

    def _initialize_history(self) -> Dict:
        """
        Initialize data collection structures.

        Returns:
            Dictionary for storing time-series data
        """
        return {
            'time': [],
            'aggregate_power': [],

            # Individual press data
            'individual_powers': {p.press_id: [] for p in self.coordinator.presses},
            'phases': {p.press_id: [] for p in self.coordinator.presses},
            'states': {p.press_id: [] for p in self.coordinator.presses},
            'phase_names': {p.press_id: [] for p in self.coordinator.presses},
            'collision_risks': {p.press_id: [] for p in self.coordinator.presses},
            'refractory_timers': {p.press_id: [] for p in self.coordinator.presses},

            # Events (sparse data)
            'delay_events': [],
            'cycle_completions': [],
            'forming_entries': [],
        }

    def reset(self):
        """Reset simulation to initial state."""
        self.coordinator.reset()
        self.history = self._initialize_history()
        self.current_time = 0.0

    def _record_timestep(self):
        """Record data for current timestep."""
        # Record time
        self.history['time'].append(self.current_time)

        # Record aggregate power
        self.history['aggregate_power'].append(self.coordinator.get_aggregate_power())

        # Record individual press data
        for press in self.coordinator.presses:
            status = press.get_status()

            self.history['individual_powers'][press.press_id].append(status['power_kw'])
            self.history['phases'][press.press_id].append(status['phase'])
            self.history['states'][press.press_id].append(status['state'])
            self.history['phase_names'][press.press_id].append(status['phase_name'])
            self.history['collision_risks'][press.press_id].append(status['collision_risk'])
            self.history['refractory_timers'][press.press_id].append(status['refractory_timer'])

    def _record_events(self):
        """Record discrete events that occurred this timestep."""
        for press in self.coordinator.presses:
            # Check for delay events
            if press.is_delaying and press.additional_delay > 0:
                self.history['delay_events'].append({
                    'time': self.current_time,
                    'press_id': press.press_id,
                    'delay_sec': press.additional_delay,
                })

            # Check for cycle completions (phase wrapped around)
            if press.prev_phase > 0.6 and press.phase < press.prev_phase:
                self.history['cycle_completions'].append({
                    'time': self.current_time,
                    'press_id': press.press_id,
                    'cycle_count': press.cycle_count,
                })

            # Check for forming phase entry
            if press.just_entered_forming():
                self.history['forming_entries'].append({
                    'time': self.current_time,
                    'press_id': press.press_id,
                })

    def step(self, dt: float = DEFAULT_TIMESTEP_SEC):
        """
        Execute one simulation timestep.

        Args:
            dt: Timestep in seconds
        """
        # Record state BEFORE stepping
        self._record_timestep()
        self._record_events()

        # Advance simulation
        self.coordinator.step(dt)

        # Update time
        self.current_time += dt

    def run(
        self,
        duration_sec: float = 300.0,
        dt: float = DEFAULT_TIMESTEP_SEC,
        verbose: bool = False
    ) -> Dict:
        """
        Run simulation for specified duration.

        Args:
            duration_sec: Simulation duration in seconds
            dt: Timestep in seconds
            verbose: Print progress messages

        Returns:
            Dictionary with simulation results and history
        """
        num_steps = int(duration_sec / dt)

        if verbose:
            print(f"Running simulation for {duration_sec}s ({num_steps} steps)")
            print(f"  Presses: {len(self.coordinator.presses)}")
            print(f"  Topology: {self.coordinator.topology_type}")
            print(f"  Timestep: {dt}s")

        for step_idx in range(num_steps):
            self.step(dt)

            # Progress updates
            if verbose and (step_idx + 1) % 1000 == 0:
                progress = (step_idx + 1) / num_steps * 100
                print(f"  Progress: {progress:.1f}%")

        if verbose:
            print("Simulation complete!")

        # Return results package
        return self.get_results()

    def get_results(self) -> Dict:
        """
        Get simulation results.

        Returns:
            Dictionary containing:
            - history: Time-series data
            - metadata: Simulation metadata
            - press_configs: Press configuration info
        """
        return {
            'history': self.history,
            'metadata': {
                'duration_sec': self.current_time,
                'num_steps': len(self.history['time']),
                'num_presses': len(self.coordinator.presses),
                'topology': self.coordinator.topology_type,
                'pacemaker': self.coordinator.pacemaker.press_id,
            },
            'press_configs': {
                press.press_id: {
                    'press_type': press.power_profile.press_type,
                    'capacity_tons': press.power_profile.capacity_tons,
                    'cycle_time_sec': press.cycle_time,
                    'peak_power_kw': press.power_profile.peak_power_kw,
                    'is_pacemaker': press.is_pacemaker,
                }
                for press in self.coordinator.presses
            },
            'final_press_stats': {
                press.press_id: {
                    'cycle_count': press.cycle_count,
                    'delay_count': press.delay_count,
                    'collisions_avoided': press.collision_avoided,
                    'total_delay_added': press.total_delay_added,
                    'final_phase': press.phase,
                }
                for press in self.coordinator.presses
            }
        }

    def get_timeseries_arrays(self) -> Dict[str, np.ndarray]:
        """
        Get time-series data as numpy arrays (useful for analysis/ML).

        Returns:
            Dictionary of numpy arrays
        """
        return {
            'time': np.array(self.history['time']),
            'aggregate_power': np.array(self.history['aggregate_power']),
            'individual_powers': {
                press_id: np.array(powers)
                for press_id, powers in self.history['individual_powers'].items()
            },
            'phases': {
                press_id: np.array(phases)
                for press_id, phases in self.history['phases'].items()
            },
            'collision_risks': {
                press_id: np.array(risks)
                for press_id, risks in self.history['collision_risks'].items()
            },
        }

    def __repr__(self) -> str:
        return (f"SimulationEngine(presses={len(self.coordinator.presses)}, "
                f"current_time={self.current_time:.1f}s, "
                f"steps={len(self.history['time'])})")
