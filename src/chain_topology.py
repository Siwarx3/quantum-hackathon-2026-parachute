"""Task 2A — Linear Chain topology, 5 qubits, with routed CPW couplers.

Coupling map:
Q1 -- Q2 -- Q3 -- Q4 -- Q5

Purpose:
A 1D nearest-neighbor hardware architecture. Fabrication-friendly
because routing is strictly planar and local with no high-degree central hub.
Workload match: 1D Trotterized Hamiltonian simulation and QAOA on line graphs.
"""
import os
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

LINEAR_EDGES = [("Q1", "Q2"), ("Q2", "Q3"), ("Q3", "Q4"), ("Q4", "Q5")]


def build_chain(pitch_mm=2.5):
    """Build the routed five-qubit linear-chain topology."""
    design = designs.DesignPlanar()
    design.overwrite_enabled = True

    design.chips.main.size.size_x = CHIP_SIZE_X
    design.chips.main.size.size_y = CHIP_SIZE_Y

    design.variables["cpw_width"] = CPW_WIDTH
    design.variables["cpw_gap"] = CPW_GAP

    positions = [
        (-2 * pitch_mm, 0),
        (-1 * pitch_mm, 0),
        (0, 0),
        (1 * pitch_mm, 0),
        (2 * pitch_mm, 0),
    ]

    for i, (x, y) in enumerate(positions, start=1):
        TransmonPocket(
            design,
            f"Q{i}",
            options=Dict(
                pos_x=f"{x}mm",
                pos_y=f"{y}mm",
                pad_width="425um",
                pad_height="90um",
                pocket_width="650um",
                pocket_height="650um",
                connection_pads=Dict(
                    a=Dict(loc_W=1, loc_H=1),
                    b=Dict(loc_W=-1, loc_H=1),
                ),
            ),
        )

    design.rebuild()

    routes = {}
    for src, dst in LINEAR_EDGES:
        rname = f"route_{src}_{dst}"
        routes[rname] = RoutePathfinder(
            design,
            rname,
            options=Dict(
                pin_inputs=Dict(
                    start_pin=Dict(component=src, pin="a"),
                    end_pin=Dict(component=dst, pin="b"),
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
    design, routes = build_chain(pitch_mm=2.5)

    root = Path(__file__).resolve().parents[1]
    out = root / "figures"
    out.mkdir(exist_ok=True)

    fig = qm.view(design)
    fig.savefig(out / "task2_linear_chain.png", dpi=180, bbox_inches="tight")

    per_coupler = {r: float(design.components[r].length) for r in routes}
    total_len_mm = sum(per_coupler.values())

    print("=== Task 2A: Linear Chain Topology ===")
    print("Coupling edges:", LINEAR_EDGES)
    print("Routes:", list(routes.keys()))
    print("Measured per-coupler lengths (mm):", per_coupler)
    print(f"Total routing length: {total_len_mm:.3f} mm")
