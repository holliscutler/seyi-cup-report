"""
Scenario Configuration and Builders

Provides ScenarioConfig dataclass and factory functions for generating
test scenarios systematically.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import itertools


@dataclass
class ScenarioConfig:
    """
    Configuration for a single test scenario.

    Attributes:
        name: Human-readable scenario name
        n_presses: Number of presses (4-8 typical)
        mix: Fleet composition ('realistic', 'varied', 'uniform', 'small', 'large')
        topology: Network topology ('ring', 'line', 'all_to_all', 'star')
        duration_sec: Simulation duration in seconds
        max_delay_sec: Maximum coordination delay allowed
        variation: Random variation to apply to profiles (0.0-0.2)
        seed: Random seed for reproducibility
    """
    name: str
    n_presses: int
    mix: str
    topology: str
    duration_sec: float
    max_delay_sec: float
    variation: float
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        return (f"Scenario('{self.name}', presses={self.n_presses}, "
                f"mix={self.mix}, seed={self.seed})")


# =============================================================================
# Factory Functions
# =============================================================================

def create_single_scenario(
    n_presses: int = 6,
    mix: str = 'realistic',
    topology: str = 'ring',
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1,
    seed: int = 42,
    name: Optional[str] = None
) -> ScenarioConfig:
    """
    Create a single scenario configuration.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        topology: Network topology
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation
        seed: Random seed
        name: Optional custom name

    Returns:
        ScenarioConfig instance
    """
    if name is None:
        name = f"{n_presses}press_{mix}_{topology}_seed{seed}"

    return ScenarioConfig(
        name=name,
        n_presses=n_presses,
        mix=mix,
        topology=topology,
        duration_sec=duration_sec,
        max_delay_sec=max_delay_sec,
        variation=variation,
        seed=seed
    )


def create_seed_sweep(
    n_presses: int,
    mix: str,
    topology: str,
    seeds: List[int],
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create multiple scenarios sweeping across seeds.

    Useful for testing statistical significance.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        topology: Network topology
        seeds: List of seeds to test
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation

    Returns:
        List of ScenarioConfig instances
    """
    scenarios = []
    for seed in seeds:
        name = f"{n_presses}p_{mix}_{topology}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios


def create_press_count_sweep(
    presses_list: List[int],
    mix: str,
    topology: str,
    seed: int = 42,
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create scenarios sweeping across different press counts.

    Useful for testing scalability.

    Args:
        presses_list: List of press counts to test
        mix: Fleet composition
        topology: Network topology
        seed: Random seed
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation

    Returns:
        List of ScenarioConfig instances
    """
    scenarios = []
    for n_presses in presses_list:
        name = f"{n_presses}p_{mix}_{topology}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios


def create_scenario_grid(
    presses_list: List[int],
    seeds: List[int],
    mix: str = 'realistic',
    topology: str = 'ring',
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create a grid of scenarios: all combinations of presses × seeds.

    This is the most common pattern for comprehensive testing.

    Args:
        presses_list: List of press counts
        seeds: List of seeds
        mix: Fleet composition
        topology: Network topology
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation

    Returns:
        List of ScenarioConfig instances (len = len(presses_list) × len(seeds))

    Example:
        >>> scenarios = create_scenario_grid([4, 5, 6], [42, 123, 456])
        >>> len(scenarios)
        9  # 3 press counts × 3 seeds
    """
    scenarios = []
    for n_presses, seed in itertools.product(presses_list, seeds):
        name = f"{n_presses}p_{mix}_{topology}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios


def create_topology_comparison(
    n_presses: int,
    mix: str,
    seed: int = 42,
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create scenarios comparing different topologies.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        seed: Random seed
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation

    Returns:
        List of ScenarioConfig instances (one per topology)
    """
    topologies = ['ring', 'line', 'all_to_all', 'star']
    scenarios = []

    for topology in topologies:
        name = f"{n_presses}p_{mix}_{topology}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios


def create_delay_sweep(
    n_presses: int,
    mix: str,
    topology: str,
    delay_values: List[float],
    seed: int = 42,
    duration_sec: float = 1800.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create scenarios sweeping across different max_delay values.

    Useful for understanding delay budget impact.

    Args:
        n_presses: Number of presses
        mix: Fleet composition
        topology: Network topology
        delay_values: List of max_delay_sec values to test
        seed: Random seed
        duration_sec: Simulation duration
        variation: Random variation

    Returns:
        List of ScenarioConfig instances
    """
    scenarios = []
    for max_delay_sec in delay_values:
        name = f"{n_presses}p_{mix}_{topology}_d{max_delay_sec}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios


def create_mix_comparison(
    n_presses: int,
    topology: str,
    seed: int = 42,
    duration_sec: float = 1800.0,
    max_delay_sec: float = 5.0,
    variation: float = 0.1
) -> List[ScenarioConfig]:
    """
    Create scenarios comparing different fleet mixes.

    Args:
        n_presses: Number of presses
        topology: Network topology
        seed: Random seed
        duration_sec: Simulation duration
        max_delay_sec: Max coordination delay
        variation: Random variation

    Returns:
        List of ScenarioConfig instances (one per mix)
    """
    mixes = ['realistic', 'varied', 'uniform', 'small', 'large']
    scenarios = []

    for mix in mixes:
        name = f"{n_presses}p_{mix}_{topology}_s{seed}"
        scenarios.append(
            ScenarioConfig(
                name=name,
                n_presses=n_presses,
                mix=mix,
                topology=topology,
                duration_sec=duration_sec,
                max_delay_sec=max_delay_sec,
                variation=variation,
                seed=seed
            )
        )
    return scenarios
