"""
Cardiac Coordinator

Manages a collection of cardiac presses and their coordination network.
Separates coordination setup from simulation execution.
"""

from typing import List, Optional, Dict
import numpy as np

from ..press import CardiacPress, PressConfig
from ..power_profiles import PowerProfile, create_power_profile, create_press_fleet
from .topology import setup_topology, get_topology_info


class CardiacCoordinator:
    """
    Coordinates multiple servo presses using cardiac rhythm principles.

    Responsibilities:
    - Create and manage cardiac presses
    - Setup network topology
    - Establish entrainment hierarchy (pacemaker)
    - Provide press access for simulation

    Key Cardiac Principles:
    1. Entrainment hierarchy (fastest press is pacemaker)
    2. Complete cycles at constant speed
    3. Adjust inter-cycle rest periods
    4. Predict and avoid collisions via network sensing
    """

    def __init__(
        self,
        press_configs: List[PressConfig],
        topology: str = 'ring',
        seed: Optional[int] = None
    ):
        """
        Initialize cardiac coordinator.

        Args:
            press_configs: List of PressConfig objects
            topology: Network topology ('ring', 'line', 'all_to_all', 'star')
            seed: Random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)

        if not press_configs:
            raise ValueError("Must provide at least one press configuration")

        self.topology_type = topology
        self.seed = seed

        # Create cardiac presses from configs
        self.presses: List[CardiacPress] = [
            CardiacPress(config) for config in press_configs
        ]

        # Setup entrainment hierarchy (pacemaker)
        self._setup_entrainment_hierarchy()

        # Setup network topology
        setup_topology(self.presses, topology)

        # Store topology info
        self.topology_info = get_topology_info(self.presses)

    def _setup_entrainment_hierarchy(self):
        """
        Setup cardiac entrainment hierarchy.

        The fastest press (shortest cycle time) becomes the pacemaker,
        similar to the SA node in the heart.
        """
        # Find fastest press (shortest cycle time)
        fastest_press = min(self.presses, key=lambda p: p.cycle_time)

        # Set as pacemaker
        fastest_press.set_pacemaker(is_pacemaker=True)

        # Others entrain to pacemaker
        for press in self.presses:
            if press.press_id != fastest_press.press_id:
                press.set_pacemaker(is_pacemaker=False, pacemaker_ref=fastest_press)

        self.pacemaker = fastest_press

    def get_aggregate_power(self) -> float:
        """
        Calculate total power draw across all presses.

        Returns:
            Total power in kW
        """
        return sum(press.get_power_kw() for press in self.presses)

    def step(self, dt: float = 0.5):
        """
        Advance all presses by one timestep.

        Args:
            dt: Timestep in seconds
        """
        for press in self.presses:
            press.step(dt)

    def reset(self):
        """Reset all presses to initial state."""
        for press in self.presses:
            press.reset()

    def get_all_status(self) -> Dict[str, Dict]:
        """
        Get status of all presses.

        Returns:
            Dictionary mapping press_id to status dict
        """
        return {
            press.press_id: press.get_status()
            for press in self.presses
        }

    def get_summary(self) -> str:
        """
        Get human-readable summary of coordinator setup.

        Returns:
            Summary string
        """
        summary = []
        summary.append("="*60)
        summary.append("Cardiac Coordinator Setup")
        summary.append("="*60)

        summary.append(f"\nNumber of Presses: {len(self.presses)}")
        summary.append(f"Topology: {self.topology_type}")
        summary.append(f"Pacemaker: {self.pacemaker.press_id} (cycle={self.pacemaker.cycle_time}s)")

        summary.append("\nTopology Info:")
        summary.append(f"  Total Connections: {self.topology_info['total_connections']}")
        summary.append(f"  Avg Neighbors/Press: {self.topology_info['avg_neighbors']:.1f}")

        summary.append("\nPress Fleet:")
        for press in self.presses:
            pm_marker = " [PACEMAKER]" if press.is_pacemaker else ""
            summary.append(f"  {press.press_id}{pm_marker}:")
            summary.append(f"    Type: {press.power_profile.press_type}")
            summary.append(f"    Capacity: {press.power_profile.capacity_tons}T")
            summary.append(f"    Cycle: {press.cycle_time}s")
            summary.append(f"    Peak Power: {press.power_profile.peak_power_kw}kW")
            summary.append(f"    Neighbors: {len(press.neighbors)}")

        summary.append("="*60)

        return "\n".join(summary)

    def __repr__(self) -> str:
        return (f"CardiacCoordinator(presses={len(self.presses)}, "
                f"topology={self.topology_type}, "
                f"pacemaker={self.pacemaker.press_id})")


# Convenience factory functions

def create_coordinator_from_profiles(
    power_profiles: List[PowerProfile],
    press_id_prefix: str = "Press",
    topology: str = 'ring',
    max_delay_sec: float = 5.0,
    seed: Optional[int] = None
) -> CardiacCoordinator:
    """
    Create coordinator from a list of power profiles.

    Args:
        power_profiles: List of PowerProfile instances
        press_id_prefix: Prefix for auto-generated press IDs
        topology: Network topology
        max_delay_sec: Maximum delay allowed
        seed: Random seed

    Returns:
        CardiacCoordinator instance
    """
    # Create press configs
    press_configs = []
    for i, profile in enumerate(power_profiles):
        press_id = f"{press_id_prefix}_{chr(65+i)}"  # Press_A, Press_B, etc.
        config = PressConfig(
            press_id=press_id,
            power_profile=profile,
            max_delay_sec=max_delay_sec,
        )
        press_configs.append(config)

    return CardiacCoordinator(press_configs, topology, seed)


def create_coordinator_from_templates(
    template_names: List[str],
    press_id_prefix: str = "Press",
    topology: str = 'ring',
    max_delay_sec: float = 5.0,
    variation: float = 0.0,
    seed: Optional[int] = None
) -> CardiacCoordinator:
    """
    Create coordinator from template names.

    Args:
        template_names: List of template names (e.g., ['medium_standard', 'large_slow'])
        press_id_prefix: Prefix for auto-generated press IDs
        topology: Network topology
        max_delay_sec: Maximum delay allowed
        variation: Random variation to apply to profiles
        seed: Random seed

    Returns:
        CardiacCoordinator instance
    """
    # Create power profiles
    power_profiles = [
        create_power_profile(template, variation, seed=seed+i if seed else None)
        for i, template in enumerate(template_names)
    ]

    return create_coordinator_from_profiles(
        power_profiles, press_id_prefix, topology, max_delay_sec, seed
    )


def create_coordinator_auto(
    n_presses: int = 4,
    mix: str = 'realistic',
    topology: str = 'ring',
    max_delay_sec: float = 5.0,
    variation: float = 0.1,
    seed: Optional[int] = None
) -> CardiacCoordinator:
    """
    Automatically create a coordinator with a press fleet.

    Convenience function for quick setup.

    Args:
        n_presses: Number of presses (4-8 typical)
        mix: Fleet composition ('uniform', 'varied', 'realistic', 'small', 'large')
        topology: Network topology
        max_delay_sec: Maximum delay allowed
        variation: Random variation to apply
        seed: Random seed

    Returns:
        CardiacCoordinator instance

    Example:
        >>> coord = create_coordinator_auto(n_presses=6, mix='realistic', seed=42)
        >>> print(coord.get_summary())
    """
    # Create press fleet
    power_profiles = create_press_fleet(n_presses, mix, variation, seed)

    return create_coordinator_from_profiles(
        power_profiles,
        press_id_prefix="Press",
        topology=topology,
        max_delay_sec=max_delay_sec,
        seed=seed
    )


def create_baseline_coordinator(
    press_configs: List[PressConfig],
    topology: str = 'ring',
    seed: Optional[int] = None
) -> CardiacCoordinator:
    """
    Create baseline coordinator with NO coordination (max_delay=0).

    Useful for comparison against cardiac coordination.

    Args:
        press_configs: List of PressConfig objects
        topology: Network topology
        seed: Random seed

    Returns:
        CardiacCoordinator with coordination disabled
    """
    # Set all max_delay to 0
    baseline_configs = []
    for config in press_configs:
        baseline_config = PressConfig(
            press_id=config.press_id,
            power_profile=config.power_profile,
            initial_phase=config.initial_phase,
            max_delay_sec=0.0,  # NO DELAY = NO COORDINATION
            is_pacemaker=config.is_pacemaker
        )
        baseline_configs.append(baseline_config)

    return CardiacCoordinator(baseline_configs, topology, seed)
