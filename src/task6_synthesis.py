"""Task 6 — Comparative synthesis and fabrication recommendation.

Builds one final table that combines:
- physical route metrics
- DRC status
- crossing / airbridge count
- EM-aware proxy interpretation
- graph/workload suitability
- explicit fabrication recommendation

This is a synthesis layer, not a new simulation.
"""

from itertools import combinations

import pandas as pd

from .topologies import edges_for_topology, degree_stats, shortest_path_length


WORKLOAD_FIT = {
    "linear": (
        "Best fit: nearest-neighbor / 1D Trotter / line-like QAOA workloads. "
        "Long-range interactions require multiple hops."
    ),
    "star": (
        "Best fit: GHZ-style, central-control, or hub-and-spoke workloads. "
        "Outer-to-outer interactions pass through Q1."
    ),
}

FABRICATION_ROLE = {
    "linear": (
        "Recommended first fabrication-development candidate: shortest routing, "
        "larger clearance, degree-2 wiring, and lower hub congestion."
    ),
    "star": (
        "Useful workload-specific candidate for central-control experiments, "
        "but higher hub density and smaller route-clearance margin increase risk."
    ),
}


def graph_diameter(topology: str, n_qubits: int = 5) -> int:
    """Return maximum shortest-path distance between any two qubits."""
    edges = edges_for_topology(topology)
    return max(
        shortest_path_length(n_qubits, edges, a, b)
        for a, b in combinations(range(n_qubits), 2)
    )


def average_shortest_path(topology: str, n_qubits: int = 5) -> float:
    """Return average shortest-path distance between all qubit pairs."""
    edges = edges_for_topology(topology)
    distances = [
        shortest_path_length(n_qubits, edges, a, b)
        for a, b in combinations(range(n_qubits), 2)
    ]
    return sum(distances) / len(distances)


def build_task6_synthesis(best_df: pd.DataFrame, em_df: pd.DataFrame) -> pd.DataFrame:
    """Create final Task-6 comparison table."""

    merged = best_df.merge(
        em_df[
            [
                "topology",
                "crossing_airbridges_needed",
                "crosstalk_risk_proxy",
                "resonator_interpretation",
            ]
        ],
        on="topology",
        how="left",
    )

    rows = []

    for row in merged.itertuples():
        topology = row.topology
        stats = degree_stats(5, edges_for_topology(topology))

        rows.append(
            {
                "topology": topology,
                "selected_layout_parameter_mm": float(row.layout_parameter_mm),
                "number_of_qubits": 5,
                "number_of_edges": len(edges_for_topology(topology)),
                "max_degree": stats["max_degree"],
                "graph_diameter": graph_diameter(topology),
                "average_shortest_path": round(average_shortest_path(topology), 3),
                "total_route_length_mm": round(float(row.total_route_length_mm), 3),
                "longest_route_or_weakest_path_proxy_mm": round(float(row.longest_route_mm), 3),
                "crossings": int(row.crossings),
                "airbridges_needed": int(row.crossing_airbridges_needed),
                "min_route_clearance_mm": round(float(row.min_route_clearance_mm), 3),
                "drc_status": "PASS" if int(row.drc_violations) == 0 else "FAIL",
                "crosstalk_risk_proxy": row.crosstalk_risk_proxy,
                "workload_fit": WORKLOAD_FIT[topology],
                "fabrication_recommendation_role": FABRICATION_ROLE[topology],
            }
        )

    df = pd.DataFrame(rows)

    # Single explicit decision for the report.
    df["final_fabrication_recommendation"] = (
        "Recommend Linear as the first fabrication-development candidate under our route-length, "
        "clearance, and DRC metrics. Star remains preferred for experiments dominated by fixed hub-to-leaf interactions."
    )

    return df


def write_task6_recommendation(root, synthesis_df: pd.DataFrame) -> None:
    """Write a short human-readable Task-6 recommendation note."""

    linear = synthesis_df[synthesis_df["topology"] == "linear"].iloc[0]
    star = synthesis_df[synthesis_df["topology"] == "star"].iloc[0]

    text = f"""# Task 6 — Comparative Synthesis and Recommendation

## Final comparison

| Metric | Linear | Star |
|---|---:|---:|
| Selected parameter | {linear.selected_layout_parameter_mm:.2f} mm | {star.selected_layout_parameter_mm:.2f} mm |
| Total route length | {linear.total_route_length_mm:.3f} mm | {star.total_route_length_mm:.3f} mm |
| Longest route / weakest-path proxy | {linear.longest_route_or_weakest_path_proxy_mm:.3f} mm | {star.longest_route_or_weakest_path_proxy_mm:.3f} mm |
| Crossings | {linear.crossings} | {star.crossings} |
| Airbridges needed | {linear.airbridges_needed} | {star.airbridges_needed} |
| Minimum route clearance | {linear.min_route_clearance_mm:.3f} mm | {star.min_route_clearance_mm:.3f} mm |
| Maximum graph degree | {linear.max_degree} | {star.max_degree} |
| Graph diameter | {linear.graph_diameter} | {star.graph_diameter} |
| DRC status | {linear.drc_status} | {star.drc_status} |

## Interpretation

The Linear Chain is the safer first fabrication-development candidate because it has shorter total routing, a shorter longest-route proxy, larger route clearance, zero crossings, zero airbridges, and lower central congestion.

The Star topology has a smaller graph diameter and direct hub-to-leaf connectivity, so it is useful for GHZ-style or central-control workloads. However, it concentrates routing and coupling around Q1, has smaller route-clearance margin, and carries higher hub-density/crosstalk-risk proxy.

## Final recommendation

Recommend the **Linear Chain** as the first fabrication-development candidate under our route-length, clearance, and DRC metrics.

The **Star** topology remains preferred for experiments dominated by fixed hub-to-leaf interactions.
"""

    (root / "reports/task6_recommendation.md").write_text(text)
