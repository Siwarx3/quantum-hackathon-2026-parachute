import numpy as np
import pandas as pd

from .design_rules import DesignRules
from .topologies import TOPOLOGIES, positions_for_topology
from .geometry_metrics import evaluate_layout


DEFAULT_WEIGHTS = {
    "total_route_length_mm": 0.20,
    "longest_route_mm": 0.15,
    "crossings": 0.20,
    "drc_violations": 0.25,
    "crosstalk_proxy": 0.15,
    "workload_mismatch": 0.05,
}


def add_normalized_cost(df, weights=None):
    weights = weights or DEFAULT_WEIGHTS
    df = df.copy()

    for metric in weights:
        values = df[metric].astype(float)
        min_v = values.min()
        max_v = values.max()

        if abs(max_v - min_v) < 1e-12:
            df[f"norm_{metric}"] = 0.0
        else:
            df[f"norm_{metric}"] = (values - min_v) / (max_v - min_v)

    df["cost"] = 0.0

    for metric, weight in weights.items():
        df["cost"] += weight * df[f"norm_{metric}"]

    return df.sort_values(["cost", "drc_violations", "crossings"]).reset_index(drop=True)


def run_sweep(
    workload="GHZ",
    rules=None,
    topologies=None,
    pitch_values=None,
    meander_values=None,
    weights=None,
):
    """
    Grid search over:
    - topology
    - qubit pitch
    - meander density

    This is transparent optimization, suitable for a hackathon.
    """

    rules = rules or DesignRules()
    topologies = topologies or list(TOPOLOGIES.keys())

    if pitch_values is None:
        pitch_values = np.round(np.linspace(1.1, 3.1, 11), 2)

    if meander_values is None:
        meander_values = [0, 1, 2, 3]

    rows = []

    for topology in topologies:
        for pitch in pitch_values:
            for meander_density in meander_values:
                positions = positions_for_topology(topology, float(pitch))

                row = evaluate_layout(
                    topology=topology,
                    positions=positions,
                    workload=workload,
                    rules=rules,
                    meander_density=meander_density,
                )

                row["input_pitch_mm"] = float(pitch)
                rows.append(row)

    df = pd.DataFrame(rows)
    return add_normalized_cost(df, weights=weights)


def best_by_topology(df):
    df = df[df["drc_violations"] == 0]
    if df.empty:
        raise ValueError("No DRC-feasible candidates")
    idx = df.groupby("topology")["cost"].idxmin()
    return df.loc[idx].sort_values("cost").reset_index(drop=True)


def best_overall(df):
    return best_by_topology(df).iloc[0]
