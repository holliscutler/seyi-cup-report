"""
Network Topology Builders

Creates network connections between presses for cardiac coordination.
Different topologies affect how presses sense and coordinate with each other.
"""

from typing import List
from ..press import CardiacPress


def setup_ring_topology(presses: List[CardiacPress]):
    """
    Setup ring topology - each press connected to left and right neighbor.

    Best for: Most realistic factory setup, balanced information flow
    Properties: Each press has exactly 2 neighbors

    Args:
        presses: List of CardiacPress instances
    """
    n = len(presses)

    if n < 3:
        raise ValueError("Ring topology requires at least 3 presses")

    for i, press in enumerate(presses):
        left_neighbor = presses[(i - 1) % n]
        right_neighbor = presses[(i + 1) % n]

        press.add_neighbor(left_neighbor)
        press.add_neighbor(right_neighbor)


def setup_line_topology(presses: List[CardiacPress]):
    """
    Setup line topology - linear chain of presses.

    Best for: Physical production line layout
    Properties: End presses have only 1 neighbor, middle presses have 2

    Args:
        presses: List of CardiacPress instances
    """
    n = len(presses)

    if n < 2:
        raise ValueError("Line topology requires at least 2 presses")

    for i, press in enumerate(presses):
        # Add left neighbor (if not first)
        if i > 0:
            press.add_neighbor(presses[i - 1])

        # Add right neighbor (if not last)
        if i < n - 1:
            press.add_neighbor(presses[i + 1])


def setup_all_to_all_topology(presses: List[CardiacPress]):
    """
    Setup all-to-all topology - every press connected to every other press.

    Best for: Maximum coordination, small fleet sizes
    Properties: Each press has (n-1) neighbors

    Warning: Can be computationally expensive for large fleets

    Args:
        presses: List of CardiacPress instances
    """
    for press in presses:
        for other in presses:
            if other.press_id != press.press_id:
                press.add_neighbor(other)


def setup_star_topology(presses: List[CardiacPress], hub_index: int = 0):
    """
    Setup star topology - one hub press connected to all others.

    Best for: Testing pacemaker effects
    Properties: Hub has (n-1) neighbors, others have only hub

    Args:
        presses: List of CardiacPress instances
        hub_index: Index of the hub press (default: 0)
    """
    n = len(presses)

    if n < 2:
        raise ValueError("Star topology requires at least 2 presses")

    if not (0 <= hub_index < n):
        raise ValueError(f"hub_index must be in [0, {n-1}], got {hub_index}")

    hub = presses[hub_index]

    for i, press in enumerate(presses):
        if i != hub_index:
            # Spoke presses connect to hub
            press.add_neighbor(hub)
            # Hub connects to spoke
            hub.add_neighbor(press)


def setup_custom_topology(presses: List[CardiacPress], connections: List[tuple[int, int]]):
    """
    Setup custom topology from connection list.

    Args:
        presses: List of CardiacPress instances
        connections: List of (index_a, index_b) tuples defining connections

    Example:
        # Create a triangle topology for 3 presses
        setup_custom_topology(presses, [(0, 1), (1, 2), (2, 0)])
    """
    n = len(presses)

    for a, b in connections:
        if not (0 <= a < n and 0 <= b < n):
            raise ValueError(f"Connection indices must be in [0, {n-1}]")

        if a != b:
            # Create bidirectional connection
            presses[a].add_neighbor(presses[b])
            presses[b].add_neighbor(presses[a])


def get_topology_info(presses: List[CardiacPress]) -> dict:
    """
    Get information about the current network topology.

    Args:
        presses: List of CardiacPress instances

    Returns:
        Dictionary with topology statistics
    """
    n = len(presses)

    neighbor_counts = [len(press.neighbors) for press in presses]

    return {
        'num_presses': n,
        'total_connections': sum(neighbor_counts) // 2,  # Divide by 2 (bidirectional)
        'avg_neighbors': sum(neighbor_counts) / n if n > 0 else 0,
        'min_neighbors': min(neighbor_counts) if neighbor_counts else 0,
        'max_neighbors': max(neighbor_counts) if neighbor_counts else 0,
        'neighbor_distribution': neighbor_counts,
    }


# Topology registry
TOPOLOGY_BUILDERS = {
    'ring': setup_ring_topology,
    'line': setup_line_topology,
    'all_to_all': setup_all_to_all_topology,
    'star': setup_star_topology,
}


def setup_topology(presses: List[CardiacPress], topology: str, **kwargs):
    """
    Setup network topology between presses.

    Args:
        presses: List of CardiacPress instances
        topology: Topology type ('ring', 'line', 'all_to_all', 'star', 'custom')
        **kwargs: Additional arguments for specific topologies

    Example:
        setup_topology(presses, 'ring')
        setup_topology(presses, 'star', hub_index=2)
        setup_topology(presses, 'custom', connections=[(0,1), (1,2)])
    """
    if topology == 'custom':
        connections = kwargs.get('connections')
        if connections is None:
            raise ValueError("Custom topology requires 'connections' parameter")
        setup_custom_topology(presses, connections)

    elif topology in TOPOLOGY_BUILDERS:
        TOPOLOGY_BUILDERS[topology](presses, **kwargs)

    else:
        raise ValueError(f"Unknown topology: {topology}. "
                        f"Valid options: {list(TOPOLOGY_BUILDERS.keys()) + ['custom']}")
