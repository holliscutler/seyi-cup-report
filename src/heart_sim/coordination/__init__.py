"""
Coordination Module

Network topology and cardiac coordination for servo presses.
"""

from .topology import (
    setup_topology,
    setup_ring_topology,
    setup_line_topology,
    setup_all_to_all_topology,
    setup_star_topology,
    setup_custom_topology,
    get_topology_info,
)

from .coordinator import (
    CardiacCoordinator,
    create_coordinator_from_profiles,
    create_coordinator_from_templates,
    create_coordinator_auto,
    create_baseline_coordinator,
)

__all__ = [
    # Topology functions
    'setup_topology',
    'setup_ring_topology',
    'setup_line_topology',
    'setup_all_to_all_topology',
    'setup_star_topology',
    'setup_custom_topology',
    'get_topology_info',

    # Coordinator
    'CardiacCoordinator',
    'create_coordinator_from_profiles',
    'create_coordinator_from_templates',
    'create_coordinator_auto',
    'create_baseline_coordinator',
]
