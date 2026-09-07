from pathlib import Path

from src.design_rules import DesignRules
from src.optimizer import run_sweep, best_by_topology, best_overall
from src.plotting import save_all_figures


def main():
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)

    rules = DesignRules()

    print("Running AQH26 Track 4 layout optimization proxy...")
    print("\nDesign rules:")

    for key, value in rules.to_dict().items():
        print(f"  {key}: {value}")

    df = run_sweep(workload="GHZ", rules=rules)
    best = best_by_topology(df)
    winner = best_overall(df)

    df.to_csv("results/sweep.csv", index=False)
    best.to_csv("results/comparison.csv", index=False)

    save_all_figures(df, best, rules)

    cols = [
        "topology",
        "input_pitch_mm",
        "meander_density",
        "n_edges",
        "max_degree",
        "total_route_length_mm",
        "longest_route_mm",
        "crossings",
        "drc_violations",
        "crosstalk_proxy",
        "workload_mismatch",
        "min_est_qw_freq_ghz",
        "cost",
        "drc_notes",
    ]

    print("\nBest candidate per topology:")
    print(best[cols].to_string(index=False))

    print("\nOverall best candidate:")
    print(winner[cols].to_string())

    print("\nSaved files:")
    print("  results/sweep.csv")
    print("  results/comparison.csv")
    print("  figures/layout_linear.png")
    print("  figures/layout_star.png")
    print("  figures/layout_ring.png")
    print("  figures/sweep_cost_vs_pitch.png")
    print("  figures/comparison_best_topologies.png")
    print("  figures/heatmap_linear.png")
    print("  figures/heatmap_star.png")
    print("  figures/heatmap_ring.png")


if __name__ == "__main__":
    main()
