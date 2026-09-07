"""Reproducible Metal sweep and submission artifacts. Run from any directory."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/aqh-mpl')
from pathlib import Path
import json
from importlib.metadata import version
import pandas as pd
import matplotlib.pyplot as plt
from src.chain_topology import build_chain
from src.star_topology import build_star
from src.metal_analysis import analyze, render

ROOT = Path(__file__).resolve().parent


def main():
    for folder in ('results', 'figures', 'reports', 'designs'):
        (ROOT / folder).mkdir(exist_ok=True)
    rows, designs = [], {}

    # Sweeping 7 standard candidate spacings (0.9 to 2.8 mm) per topology
    sweep_configs = [
        ('linear', build_chain, (0.9, 1.2, 1.5, 1.8, 2.1, 2.5, 2.8), 'chain_neighbor_pitch_mm'),
        ('star', build_star, (0.9, 1.2, 1.5, 1.8, 2.1, 2.5, 2.8), 'star_hub_to_leaf_radius_mm'),
    ]

    for topology, builder, sweep_values, sweep_var in sweep_configs:
        for pitch in sweep_values:
            print(f'Building {topology} at {pitch:.1f}mm ({sweep_var})', flush=True)
            build_failure = False
            try:
                design, routes = builder(pitch)
                result = analyze(design, routes)
                designs[topology, pitch] = design
            except Exception as exc:
                build_failure = True
                result = dict(
                    drc_violations=1,
                    drc_notes=f'Build failed: {type(exc).__name__}: {exc}',
                    total_route_length_mm=float('nan'),
                    longest_route_mm=float('nan'),
                    crossings=float('nan'),
                    min_route_clearance_mm=float('nan'),
                )

            failure_type = "none"
            if build_failure:
                failure_type = "build_failure"
            elif result["drc_violations"] > 0:
                failure_type = "drc_violation"

            sweep_variable = (
                "chain_neighbor_pitch_mm"
                if topology == "linear"
                else "star_hub_to_leaf_radius_mm"
            )

            rows.append(
                dict(
                    topology=topology,
                    pitch_mm=pitch,  # kept for report compatibility
                    layout_parameter_mm=pitch,
                    sweep_variable=sweep_variable,
                    **result,
                )
            )

    df = pd.DataFrame(rows)

    # Task 3 optimization rule:
    # Invalid layouts cannot win. Among DRC-feasible layouts,
    # minimize total built CPW route length.
    df["is_feasible"] = df["drc_violations"] == 0

    df["optimization_cost_mm"] = df.apply(
        lambda row: row["total_route_length_mm"]
        if row["is_feasible"]
        else float("inf"),
        axis=1,
    )

    df["cost_function"] = (
        "minimize total_route_length_mm subject to drc_violations == 0"
    )

    df.to_csv(ROOT / "results/metal_sweep.csv", index=False)

    feasible = df[df["is_feasible"]]

    best = (
        feasible
        .sort_values("optimization_cost_mm")
        .groupby("topology", as_index=False)
        .first()
    )

    best.to_csv(ROOT / "results/metal_comparison.csv", index=False)

    for row in best.itertuples():
        design = designs[row.topology, row.layout_parameter_mm]
        render(
            design,
            ROOT / f'figures/metal_{row.topology}.png',
            f'{row.topology}: Metal geometry, pitch/radius {row.layout_parameter_mm:.1f} mm',
        )
        # Metal's Python export recreates components without depending on pickle compatibility.
        script = design.to_python_script().replace(
            'from qiskit_metal import designs, MetalGUI',
            'from qiskit_metal import designs',
        )
        script = script.replace(
            'gui = MetalGUI(design)',
            "design.chips.main.size.size_x = '12mm'\ndesign.chips.main.size.size_y = '10mm'",
        )
        script = script[:script.index('gui.rebuild()')] + 'design.rebuild()\n'
        (ROOT / f'designs/{row.topology}.py').write_text(script)

    # Plotting Task 3 sweep curves
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for name, group in df.groupby('topology'):
        valid_pts = group[group.is_feasible]
        axes[0].plot(
            valid_pts.layout_parameter_mm,
            valid_pts.optimization_cost_mm,
            'o-',
            label=name,
            linewidth=2,
        )
        axes[1].plot(
            group.layout_parameter_mm,
            group.drc_violations,
            'o-',
            label=name,
            linewidth=2,
        )

    axes[0].set_title('Task 3: Built Route Length Objective')
    axes[0].set_ylabel('Built Route Length (mm)')
    axes[1].set_title('Task 3: Geometry Rule Violations Across Sweep')
    axes[1].set_ylabel('Number of Rule Violations')

    for ax in axes:
        ax.set_xlabel('Layout Parameter: Chain Pitch or Star Radius (mm)')
        ax.legend()
        ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(ROOT / 'figures/metal_sweep.png', dpi=180)
    plt.close(fig)

    (ROOT / 'results/environment.json').write_text(
        json.dumps(
            {
                p: version(p)
                for p in ('quantum-metal', 'numpy', 'pandas', 'matplotlib', 'shapely')
            },
            indent=2,
        )
    )

    from src.submission_report import write_report
    write_report(ROOT, df, best)
    print("\n=== Best Feasible Candidates Selected ===")
    print(best[['topology', 'layout_parameter_mm', 'total_route_length_mm', 'longest_route_mm', 'optimization_cost_mm', 'drc_violations']].to_string(index=False))

    if set(best.topology) != {'linear', 'star'}:
        raise SystemExit(
            'Incomplete: a topology has no feasible Metal candidate. See metal_sweep.csv.'
        )


if __name__ == '__main__':
    main()
