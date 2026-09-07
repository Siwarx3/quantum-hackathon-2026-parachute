import math
from collections import deque


TOPOLOGIES = {
    "linear": [(0, 1), (1, 2), (2, 3), (3, 4)],
    "star": [(0, 1), (0, 2), (0, 3), (0, 4)],
    "ring": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
}


WORKLOADS = {
    "GHZ": [(0, 1), (0, 2), (0, 3), (0, 4)],
    "QAOA_5_CYCLE": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
    "LINEAR_CHAIN": [(0, 1), (1, 2), (2, 3), (3, 4)],
}


def edges_for_topology(topology: str):
    if topology not in TOPOLOGIES:
        raise ValueError(f"Unknown topology: {topology}")
    return TOPOLOGIES[topology]


def positions_for_topology(topology: str, pitch_mm: float):
    """
    Return qubit center positions in mm.

    pitch_mm is the main layout sweep variable.
    """

    p = float(pitch_mm)

    if topology == "linear":
        return {
            0: (-2 * p, 0.0),
            1: (-1 * p, 0.0),
            2: (0.0, 0.0),
            3: (1 * p, 0.0),
            4: (2 * p, 0.0),
        }

    if topology == "star":
        return {0: (0.0, 0.0), **{i + 1: (p * math.cos(a), p * math.sin(a))
                for i, a in enumerate([math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4])}}

    if topology == "ring":
        # Circumradius chosen so adjacent qubits are about pitch_mm apart.
        radius = p / (2 * math.sin(math.pi / 5))
        positions = {}

        for i in range(5):
            theta = math.pi / 2 - 2 * math.pi * i / 5
            positions[i] = (
                radius * math.cos(theta),
                radius * math.sin(theta),
            )

        return positions

    raise ValueError(f"Unknown topology: {topology}")


def adjacency(n_qubits: int, edges):
    adj = {i: [] for i in range(n_qubits)}

    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    return adj


def shortest_path_length(n_qubits: int, edges, start: int, goal: int):
    if start == goal:
        return 0

    adj = adjacency(n_qubits, edges)
    queue = deque([(start, 0)])
    seen = {start}

    while queue:
        node, dist = queue.popleft()

        for nxt in adj[node]:
            if nxt == goal:
                return dist + 1

            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, dist + 1))

    return float("inf")


def degree_stats(n_qubits: int, edges):
    adj = adjacency(n_qubits, edges)
    degrees = {q: len(adj[q]) for q in adj}

    return {
        "max_degree": max(degrees.values()),
        "min_degree": min(degrees.values()),
        "avg_degree": sum(degrees.values()) / n_qubits,
        "degrees": degrees,
    }


def workload_mismatch_score(topology: str, workload: str):
    """
    Lower is better.

    If a workload edge is directly available in hardware, distance = 1.
    Extra distance is used as a simple routing/SWAP-overhead proxy.
    """

    if workload not in WORKLOADS:
        raise ValueError(f"Unknown workload: {workload}")

    hardware_edges = edges_for_topology(topology)
    required_edges = WORKLOADS[workload]

    penalties = []

    for a, b in required_edges:
        d = shortest_path_length(5, hardware_edges, a, b)
        penalties.append(max(d - 1, 0))

    return sum(penalties) / len(penalties)
