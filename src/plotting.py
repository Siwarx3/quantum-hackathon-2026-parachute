from pathlib import Path

import matplotlib.pyplot as plt

from .topologies import edges_for_topology, positions_for_topology


def ensure_output_dirs():
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)


def plot_layout(topology, pitch_mm, rules, meander_density=0, outfile=None):
    positions = positions_for_topology(topology, pitch_mm)
    edges = edges_for_topology(topology)

    fig, ax = plt.subplots(figsize=(6, 6))

    half_w = rules.chip_width_mm / 2
    half_h = rules.chip_height_mm / 2

    # Chip boundary.
    ax.plot(
        [-half_w, half_w, half_w, -half_w, -half_w],
        [-half_h, -half_h, half_h, half_h, -half_h],
        linewidth=1.5,
        label="chip boundary",
    )

    # Keepout boundary.
    kx = half_w - rules.edge_keepout_mm
    ky = half_h - rules.edge_keepout_mm

    ax.plot(
        [-kx, kx, kx, -kx, -kx],
        [-ky, -ky, ky, ky, -ky],
        linestyle="--",
        linewidth=1.0,
        label="edge keepout",
    )

    # Coupler/route edges.
    for a, b in edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        ax.plot([x1, x2], [y1, y2], linewidth=2)

    # Qubit centers.
    xs = [positions[q][0] for q in positions]
    ys = [positions[q][1] for q in positions]

    ax.scatter(xs, ys, s=300, zorder=3)

    for q, (x, y) in positions.items():
        ax.text(x, y, f"Q{q}", ha="center", va="center", fontsize=10)

    ax.set_title(f"{topology.title()} topology | pitch={pitch_mm:.2f} mm | meander={meander_density}")
    ax.set_xlabel("x position (mm)")
    ax.set_ylabel("y position (mm)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.4)
    ax.legend(loc="upper right", fontsize=8)

    if outfile:
        fig.savefig(outfile, dpi=220, bbox_inches="tight")

    return fig, ax


def plot_sweep_cost(df, outfile="figures/sweep_cost_vs_pitch.png"):
    best_per_pitch = (
        df.sort_values("cost")
        .groupby(["topology", "input_pitch_mm"], as_index=False)
        .first()
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    for topology, sub in best_per_pitch.groupby("topology"):
        sub = sub.sort_values("input_pitch_mm")
        ax.plot(sub["input_pitch_mm"], sub["cost"], marker="o", label=topology)

    ax.set_title("Parameter sweep: cost vs qubit pitch")
    ax.set_xlabel("Qubit pitch parameter (mm)")
    ax.set_ylabel("Normalized cost, lower is better")
    ax.grid(True, linewidth=0.4)
    ax.legend()

    fig.savefig(outfile, dpi=220, bbox_inches="tight")
    return fig, ax


def plot_best_comparison(best_df, outfile="figures/comparison_best_topologies.png"):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(best_df["topology"], best_df["cost"])

    ax.set_title("Best candidate cost by topology")
    ax.set_xlabel("Topology")
    ax.set_ylabel("Normalized cost, lower is better")
    ax.grid(True, axis="y", linewidth=0.4)

    fig.savefig(outfile, dpi=220, bbox_inches="tight")
    return fig, ax


def plot_heatmap_for_topology(df, topology, outfile=None):
    sub = df[df["topology"] == topology].copy()

    pivot = sub.pivot_table(
        index="meander_density",
        columns="input_pitch_mm",
        values="cost",
        aggfunc="min",
    )

    fig, ax = plt.subplots(figsize=(8, 4.8))
    image = ax.imshow(pivot.values, aspect="auto", origin="lower")

    ax.set_title(f"2D sweep heatmap: {topology}")
    ax.set_xlabel("Pitch value index")
    ax.set_ylabel("Meander density")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(x) for x in pivot.columns], rotation=45)

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(y) for y in pivot.index])

    fig.colorbar(image, ax=ax, label="Normalized cost")

    if outfile is None:
        outfile = f"figures/heatmap_{topology}.png"

    fig.savefig(outfile, dpi=220, bbox_inches="tight")
    return fig, ax


def save_all_figures(df, best_df, rules):
    ensure_output_dirs()

    for _, row in best_df.iterrows():
        plot_layout(
            topology=row["topology"],
            pitch_mm=float(row["input_pitch_mm"]),
            rules=rules,
            meander_density=int(row["meander_density"]),
            outfile=f"figures/layout_{row['topology']}.png",
        )

    plot_sweep_cost(df)
    plot_best_comparison(best_df)

    for topology in sorted(df["topology"].unique()):
        plot_heatmap_for_topology(df, topology)
