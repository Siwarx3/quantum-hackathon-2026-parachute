"""Task 1 — Baseline five-qubit superconducting chip in Qiskit Metal.

Creates:
- One planar chip (12 mm x 10 mm)
- Five TransmonPocket qubits placed symmetrically with pitch = 2.5 mm
- Explicit baseline CPW variables (10 um trace, 6 um gap)
- No qubit-to-qubit routing yet (routing/topology belongs to Task 2)
"""
from pathlib import Path
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ.setdefault('MPLBACKEND', 'Agg')

import qiskit_metal as qm
from qiskit_metal import designs, Dict
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket

try:
    from .design_rules import (
        CHIP_SIZE_X,
        CHIP_SIZE_Y,
        BASELINE_PITCH_MM,
        CPW_WIDTH,
        CPW_GAP,
    )
except ImportError:
    from design_rules import (
        CHIP_SIZE_X,
        CHIP_SIZE_Y,
        BASELINE_PITCH_MM,
        CPW_WIDTH,
        CPW_GAP,
    )


def build_baseline(pitch_mm=BASELINE_PITCH_MM):
    """Build and return the five-qubit Task-1 baseline design."""
    design = designs.DesignPlanar()
    design.overwrite_enabled = True

    # Define chip footprint
    design.chips.main.size.size_x = CHIP_SIZE_X
    design.chips.main.size.size_y = CHIP_SIZE_Y

    # Explicit microwave/CPW baseline geometry
    design.variables["cpw_width"] = CPW_WIDTH
    design.variables["cpw_gap"] = CPW_GAP

    # Symmetric five-qubit placement around x = 0
    positions = [
        (-2 * pitch_mm, 0),
        (-1 * pitch_mm, 0),
        (0, 0),
        (1 * pitch_mm, 0),
        (2 * pitch_mm, 0),
    ]

    qubits = {}
    for i, (x, y) in enumerate(positions, start=1):
        name = f"Q{i}"
        qubits[name] = TransmonPocket(
            design,
            name,
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

    # Convert component definitions into built Metal geometry
    design.rebuild()
    return design, qubits


if __name__ == "__main__":
    design, qubits = build_baseline()

    print("=== AQH26 Task 1 Baseline ===")
    print("Number of qubits:", len(qubits))
    print("Qubits:", list(qubits.keys()))
    print("Chip:", CHIP_SIZE_X, "x", CHIP_SIZE_Y)
    print("CPW width:", design.variables["cpw_width"])
    print("CPW gap:", design.variables["cpw_gap"])

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "renders"
    output_dir.mkdir(exist_ok=True)

    fig = qm.view(design)
    output = output_dir / "baseline_5qubit.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")

    print("Saved render:", output)
