"""Task 1: self-defined Design Rule Check (DRC) for the baseline chip design."""
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket

try:
    from .design_rules import (
        MIN_QUBIT_GAP_MM,
        MIN_CPW_WIDTH_MM,
        MIN_CPW_GAP_MM,
        EDGE_KEEPOUT_MM,
    )
except ImportError:
    from design_rules import (
        MIN_QUBIT_GAP_MM,
        MIN_CPW_WIDTH_MM,
        MIN_CPW_GAP_MM,
        EDGE_KEEPOUT_MM,
    )


def get_qubit_components(design):
    """Return {name: component} for every TransmonPocket in the design."""
    return {name: comp for name, comp in design.components.items()
            if isinstance(comp, TransmonPocket)}


def edge_to_edge_gap(bounds_a, bounds_b):
    """Gap between two axis-aligned bounding boxes. Negative means overlap."""
    ax_min, ay_min, ax_max, ay_max = bounds_a
    bx_min, by_min, bx_max, by_max = bounds_b
    dx = max(bx_min - ax_max, ax_min - bx_max, 0)
    dy = max(by_min - ay_max, ay_min - by_max, 0)
    if dx == 0 and dy == 0:
        # boxes overlap on both axes -> real overlap; report negative penetration
        overlap_x = min(ax_max, bx_max) - max(ax_min, bx_min)
        overlap_y = min(ay_max, by_max) - max(ay_min, by_min)
        return -min(overlap_x, overlap_y)
    return (dx**2 + dy**2) ** 0.5


def check_qubit_spacing(design, min_gap_mm=MIN_QUBIT_GAP_MM):
    """Rule 1: no two qubit pockets may sit closer than min_gap_mm apart, edge to edge."""
    qubits = get_qubit_components(design)
    names = list(qubits.keys())
    violations = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            b1 = qubits[n1].qgeometry_bounds()
            b2 = qubits[n2].qgeometry_bounds()
            gap = edge_to_edge_gap(b1, b2)
            if gap < min_gap_mm:
                violations.append((n1, n2, round(gap, 3)))
    return violations


def check_trace_geometry(design, min_width_mm=MIN_CPW_WIDTH_MM, min_gap_mm=MIN_CPW_GAP_MM):
    """Rule 2: CPW trace width/gap must meet our self-defined comparative minimum feature size."""
    def to_mm(val_str):
        val_str = str(val_str).strip()
        if val_str.endswith('um'):
            return float(val_str[:-2]) / 1000
        if val_str.endswith('mm'):
            return float(val_str[:-2])
        return float(val_str)

    width_mm = to_mm(design.variables.get('cpw_width', '10um'))
    gap_mm = to_mm(design.variables.get('cpw_gap', '6um'))
    violations = []
    if width_mm < min_width_mm - 1e-9:
        violations.append(('cpw_width', width_mm, min_width_mm))
    if gap_mm < min_gap_mm - 1e-9:
        violations.append(('cpw_gap', gap_mm, min_gap_mm))
    return violations


def check_keepout(design, margin_mm=EDGE_KEEPOUT_MM):
    """Rule 3: no component may sit within margin_mm of the chip edge."""
    size_x = float(design.chips.main.size.size_x.replace('mm', ''))
    size_y = float(design.chips.main.size.size_y.replace('mm', ''))
    cx = float(design.chips.main.size.center_x.replace('mm', ''))
    cy = float(design.chips.main.size.center_y.replace('mm', ''))
    chip_xmin, chip_xmax = cx - size_x/2, cx + size_x/2
    chip_ymin, chip_ymax = cy - size_y/2, cy + size_y/2

    violations = []
    qubits = get_qubit_components(design)
    for name, comp in qubits.items():
        xmin, ymin, xmax, ymax = comp.qgeometry_bounds()
        if (xmin - chip_xmin < margin_mm or chip_xmax - xmax < margin_mm or
            ymin - chip_ymin < margin_mm or chip_ymax - ymax < margin_mm):
            violations.append(name)
    return violations


def run_all_checks(design, min_qubit_gap_mm=MIN_QUBIT_GAP_MM, keepout_margin_mm=EDGE_KEEPOUT_MM):
    """Run all baseline DRC checks on the design and print a clear report."""
    print("=== DRC Report ===")
    spacing_violations = check_qubit_spacing(design, min_qubit_gap_mm)
    if spacing_violations:
        print(f"[FAIL] Qubit spacing (<{min_qubit_gap_mm}mm gap):")
        for n1, n2, gap in spacing_violations:
            print(f"    {n1} <-> {n2}: gap = {gap}mm")
    else:
        print(f"[PASS] Qubit spacing >= {min_qubit_gap_mm}mm for all pairs")

    trace_violations = check_trace_geometry(design)
    if trace_violations:
        print("[FAIL] Trace geometry below minimum feature size:")
        for name, val, minimum in trace_violations:
            print(f"    {name} = {val}mm < required {minimum}mm")
    else:
        print(f"[PASS] CPW trace width/gap meet minimum feature size (w>={MIN_CPW_WIDTH_MM*1e3:.0f}um, g>={MIN_CPW_GAP_MM*1e3:.0f}um)")

    keepout_violations = check_keepout(design, keepout_margin_mm)
    if keepout_violations:
        print(f"[FAIL] Keep-out zone violation (<{keepout_margin_mm}mm from edge): {keepout_violations}")
    else:
        print(f"[PASS] All qubits respect {keepout_margin_mm}mm keep-out from chip edge")

    all_pass = not (spacing_violations or trace_violations or keepout_violations)
    return all_pass


if __name__ == '__main__':
    try:
        from .baseline_chip import build_baseline
    except ImportError:
        from baseline_chip import build_baseline

    print(">>> TASK 1: checking baseline chip (pitch = 2.5 mm)")
    design, _ = build_baseline()
    run_all_checks(design)

    print("\n>>> TASK 1 verification: checking deliberately tight spacing (pitch = 0.5 mm)")
    design2, _ = build_baseline(pitch_mm=0.5)
    run_all_checks(design2)
