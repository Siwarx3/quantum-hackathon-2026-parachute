"""Optional Task 3 refinement.

This script refines the minimum feasible layout parameter for each topology.
It is inspired by a simple binary-search optimizer, but it uses the full
metal_analysis.analyze() validator instead of checking only qubit spacing.
"""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/aqh-mpl")

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import matplotlib.pyplot as plt

from src.chain_topology import build_chain
from src.star_topology import build_star
from src.metal_analysis import analyze


def build_candidate(topology, value):
    if topology == "linear":
        return build_chain(pitch_mm=value)
    if topology == "star":
        return build_star(radius_mm=value)
    raise ValueError(f"Unknown topology: {topology}")


def evaluate(topology, value):
    try:
        design, routes = build_candidate(topology, value)
        result = analyze(design, routes)
    except Exception as exc:
        result = dict(
            drc_violations=1,
            drc_notes=f"Build failed: {type(exc).__name__}: {exc}",
            total_route_length_mm=float("nan"),
            longest_route_mm=float("nan"),
            crossings=float("nan"),
            min_route_clearance_mm=float("nan"),
        )
    result["topology"] = topology
    result["layout_parameter_mm"] = value
    result["is_feasible"] = result["drc_violations"] == 0
    result["optimization_cost_mm"] = (
        result["total_route_length_mm"]
        if result["is_feasible"]
        else float("inf")
    )
    return result


def binary_refine(topology, lo, hi, tol=0.005):
    """Find the smallest DRC-feasible layout parameter.

    This assumes feasibility generally improves as spacing/radius increases.
    """
    history = []

    while hi - lo > tol:
        mid = (lo + hi) / 2
        row = evaluate(topology, mid)
        history.append(row)

        if row["is_feasible"]:
            hi = mid
        else:
            lo = mid

    final = evaluate(topology, hi)
    history.append(final)

    return final, history


def main():
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "figures").mkdir(exist_ok=True)

    configs = {
        "linear": (1.0, 1.5),
        "star": (1.3, 1.6),
    }

    final_rows = []
    history_rows = []

    for topology, (lo, hi) in configs.items():
        final, history = binary_refine(topology, lo, hi)
        final_rows.append(final)
        history_rows.extend(history)

        print(
            f"{topology}: refined feasible parameter = "
            f"{final['layout_parameter_mm']:.3f} mm, "
            f"cost = {final['optimization_cost_mm']:.3f} mm, "
            f"DRC = {final['drc_violations']}"
        )

    df_history = pd.DataFrame(history_rows)
    df_final = pd.DataFrame(final_rows)

    df_history.to_csv(ROOT / "results/task3_refined_search_history.csv", index=False)
    df_final.to_csv(ROOT / "results/task3_refined_best.csv", index=False)

    plt.figure(figsize=(7, 5))

    for topology, group in df_history.groupby("topology"):
        group = group.sort_values("layout_parameter_mm")
        plt.plot(
            group["layout_parameter_mm"],
            group["optimization_cost_mm"],
            marker="o",
            label=topology,
        )

    plt.xlabel("Layout parameter: chain pitch or star radius (mm)")
    plt.ylabel("Optimization cost: total route length (mm)")
    plt.title("Task 3 refined feasible-spacing search")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROOT / "figures/task3_refined_optimizer.png", dpi=180)

    print("Saved:")
    print("results/task3_refined_search_history.csv")
    print("results/task3_refined_best.csv")
    print("figures/task3_refined_optimizer.png")


if __name__ == "__main__":
    main()
