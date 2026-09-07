"""Task 2B — Star / Hub topology, 5 qubits, with routed CPW couplers.

Coupling map:
        Q2
         |
Q3 ----- Q1 ----- Q5
         |
        Q4

Purpose:
A hub-and-spoke topology where central transmon Q1 interacts directly with
all 4 outer qubits.
Workload match: Centralized GHZ state preparation and syndrome extraction.
Trade-off: Low graph diameter (2), but introduces routing and capacitive congestion
at the central 4-pad hub transmon.
"""
import os
import math
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/aqh-mpl")

from qiskit_metal import designs, Dict
import qiskit_metal as qm
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder

try:
    from .design_rules import CHIP_SIZE_X, CHIP_SIZE_Y, CPW_WIDTH, CPW_GAP
except ImportError:
    from design_rules import CHIP_SIZE_X, CHIP_SIZE_Y, CPW_WIDTH, CPW_GAP

CORNERS = {
    "ne": (1, 1),
    "nw": (-1, 1),
    "se": (1, -1),
    "sw": (-1, -1),
}

OPPOSITE = {
    "ne": "sw",
    "nw": "se",
    "se": "nw",
    "sw": "ne",
}

STAR_EDGES = [("Q1", "Q2"), ("Q1", "Q3"), ("Q1", "Q4"), ("Q1", "Q5")]


def build_star(radius_mm=2.5):
    """Build the routed five-qubit star/hub topology."""
    design = designs.DesignPlanar()
    design.overwrite_enabled = True

    design.chips.main.size.size_x = CHIP_SIZE_X
    design.chips.main.size.size_y = CHIP_SIZE_Y

    design.variables["cpw_width"] = CPW_WIDTH
    design.variables["cpw_gap"] = CPW_GAP

    # Q1 is the central hub transmon with 4 corner connection pads.
    TransmonPocket(
        design,
        "Q1",
        options=Dict(
            pos_x="0mm",
            pos_y="0mm",
            pad_width="425um",
            pad_height="90um",
            pocket_width="650um",
            pocket_height="650um",
            connection_pads=Dict(
                **{k: Dict(loc_W=w, loc_H=h) for k, (w, h) in CORNERS.items()}
            ),
        ),
    )

    # Outer leaf qubits are placed along the diagonals (45, 135, 225, 315 deg)
    # so each outer qubit's pad faces directly toward a specific corner of Q1.
    outer_dirs = ["ne", "nw", "sw", "se"]
    angle_map = {
        "ne": math.pi / 4,
        "nw": 3 * math.pi / 4,
        "sw": 5 * math.pi / 4,
        "se": 7 * math.pi / 4,
    }

    for i, direction in enumerate(outer_dirs, start=2):
        angle = angle_map[direction]
        x = radius_mm * math.cos(angle)
        y = radius_mm * math.sin(angle)

        pad_dir = OPPOSITE[direction]
        w, h = CORNERS[pad_dir]

        TransmonPocket(
            design,
            f"Q{i}",
            options=Dict(
                pos_x=f"{x:.3f}mm",
                pos_y=f"{y:.3f}mm",
                pad_width="425um",
                pad_height="90um",
                pocket_width="650um",
                pocket_height="650um",
                connection_pads=Dict(
                    p=Dict(loc_W=w, loc_H=h),
                ),
            ),
        )

    design.rebuild()

    routes = {}
    for i, direction in zip(range(2, 6), outer_dirs):
        rname = f"route_Q1_Q{i}"
        routes[rname] = RoutePathfinder(
            design,
            rname,
            options=Dict(
                pin_inputs=Dict(
                    start_pin=Dict(component="Q1", pin=direction),
                    end_pin=Dict(component=f"Q{i}", pin="p"),
                ),
                trace_width=CPW_WIDTH,
                trace_gap=CPW_GAP,
                lead=Dict(start_straight="100um", end_straight="100um"),
                fillet="50um",
            ),
        )

    design.rebuild()
    return design, routes


if __name__ == "__main__":
    design, routes = build_star(radius_mm=2.5)

    root = Path(__file__).resolve().parents[1]
    out = root / "figures"
    out.mkdir(exist_ok=True)

    fig = qm.view(design)
    fig.savefig(out / "task2_star_hub.png", dpi=180, bbox_inches="tight")

    per_coupler = {r: float(design.components[r].length) for r in routes}
    total_len_mm = sum(per_coupler.values())

    print("=== Task 2B: Star Hub Topology ===")
    print("Coupling edges:", STAR_EDGES)
    print("Routes:", list(routes.keys()))
    print("Measured per-coupler lengths (mm):", per_coupler)
    print(f"Total routing length: {total_len_mm:.3f} mm")
