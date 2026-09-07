import math
from itertools import combinations

from .topologies import edges_for_topology, degree_stats, workload_mismatch_score


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def route_length_mm(a, b, meander_density=0):
    """
    Route length proxy.

    meander_density increases electrical path length.
    This is a geometric estimate, not full EM simulation.
    """

    base = distance(a, b)
    return base * (1.0 + 0.10 * float(meander_density))


def orientation(a, b, c):
    value = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])

    if abs(value) < 1e-12:
        return 0

    return 1 if value > 0 else 2


def on_segment(a, b, c):
    return (
        min(a[0], c[0]) <= b[0] <= max(a[0], c[0])
        and min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
    )


def segments_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, p2, q1):
        return True

    if o2 == 0 and on_segment(p1, q2, q1):
        return True

    if o3 == 0 and on_segment(p2, p1, q2):
        return True

    if o4 == 0 and on_segment(p2, q1, q2):
        return True

    return False


def point_to_segment_distance(point, a, b):
    px, py = point
    ax, ay = a
    bx, by = b

    dx = bx - ax
    dy = by - ay

    if abs(dx) < 1e-12 and abs(dy) < 1e-12:
        return distance(point, a)

    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    proj = (ax + t * dx, ay + t * dy)
    return distance(point, proj)


def segment_distance(a, b, c, d):
    if segments_intersect(a, b, c, d):
        return 0.0

    return min(
        point_to_segment_distance(a, c, d),
        point_to_segment_distance(b, c, d),
        point_to_segment_distance(c, a, b),
        point_to_segment_distance(d, a, b),
    )


def route_parallelness(a, b, c, d):
    """
    1 = parallel or anti-parallel.
    0 = perpendicular.
    """

    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (d[0] - c[0], d[1] - c[1])

    n1 = math.hypot(v1[0], v1[1])
    n2 = math.hypot(v2[0], v2[1])

    if n1 == 0 or n2 == 0:
        return 0.0

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    return abs(dot / (n1 * n2))


def count_crossings(positions, edges):
    crossings = 0

    for e1, e2 in combinations(edges, 2):
        # Routes sharing a qubit are connected by design, not counted as crossings.
        if set(e1) & set(e2):
            continue

        a, b = positions[e1[0]], positions[e1[1]]
        c, d = positions[e2[0]], positions[e2[1]]

        if segments_intersect(a, b, c, d):
            crossings += 1

    return crossings


def crosstalk_risk_proxy(positions, edges, rules, meander_density=0):
    """
    Geometry-based crosstalk-risk proxy.

    Risk increases when:
    - independent routes are close,
    - close routes are parallel,
    - meander density increases,
    - topology has a high-degree central hub.

    This is NOT measured crosstalk.
    """

    risk = 0.0

    for e1, e2 in combinations(edges, 2):
        if set(e1) & set(e2):
            continue

        a, b = positions[e1[0]], positions[e1[1]]
        c, d = positions[e2[0]], positions[e2[1]]

        sep = segment_distance(a, b, c, d)
        parallel = route_parallelness(a, b, c, d)

        threshold = 2.0 * rules.min_route_spacing_mm

        if sep < threshold:
            risk += ((threshold - sep) / rules.min_route_spacing_mm) * (0.5 + parallel)

    stats = degree_stats(5, edges)

    hub_penalty = max(0, stats["max_degree"] - 2) * 0.50
    meander_penalty = len(edges) * 0.05 * float(meander_density)

    return risk + hub_penalty + meander_penalty


def estimate_quarter_wave_frequency_ghz(length_mm, eps_eff=6.0):
    """
    Rough quarter-wave estimate:

        f ~= vp / (4L)
        vp ~= c / sqrt(eps_eff)

    This is only an EM-aware estimate, not a solver result.
    """

    if length_mm <= 0:
        return float("inf")

    c = 299_792_458.0
    vp = c / math.sqrt(eps_eff)
    length_m = length_mm * 1e-3

    return vp / (4.0 * length_m) / 1e9


def drc_violations(positions, edges, rules):
    violations = []

    half_w = rules.chip_width_mm / 2
    half_h = rules.chip_height_mm / 2

    # Edge keepout.
    for q, (x, y) in positions.items():
        if abs(x) > half_w - rules.edge_keepout_mm:
            violations.append(f"Q{q} violates x-edge keepout")

        if abs(y) > half_h - rules.edge_keepout_mm:
            violations.append(f"Q{q} violates y-edge keepout")

    # Qubit spacing.
    for q1, q2 in combinations(positions.keys(), 2):
        d = distance(positions[q1], positions[q2])

        if d < rules.min_qubit_spacing_mm:
            violations.append(
                f"Q{q1}-Q{q2} spacing {d:.3f} mm < {rules.min_qubit_spacing_mm:.3f} mm"
            )

    # CPW design rules.
    if rules.cpw_width_um < rules.min_cpw_width_um:
        violations.append("CPW width below minimum")

    if rules.cpw_gap_um < rules.min_cpw_gap_um:
        violations.append("CPW gap below minimum")

    # Crossing and route-spacing checks.
    for e1, e2 in combinations(edges, 2):
        if set(e1) & set(e2):
            continue

        a, b = positions[e1[0]], positions[e1[1]]
        c, d = positions[e2[0]], positions[e2[1]]

        if segments_intersect(a, b, c, d):
            violations.append(f"Route {e1} crosses route {e2}")

        sep = segment_distance(a, b, c, d)

        if sep < rules.min_route_spacing_mm:
            violations.append(
                f"Route {e1} too close to route {e2}: {sep:.3f} mm < {rules.min_route_spacing_mm:.3f} mm"
            )

    return violations


def evaluate_layout(topology, positions, workload, rules, meander_density=0):
    edges = edges_for_topology(topology)

    lengths = [
        route_length_mm(
            positions[a],
            positions[b],
            meander_density=meander_density,
        )
        for a, b in edges
    ]

    total_length = sum(lengths)
    longest = max(lengths) if lengths else 0.0
    crossings = count_crossings(positions, edges)
    violations = drc_violations(positions, edges, rules)
    xtalk = crosstalk_risk_proxy(positions, edges, rules, meander_density)

    stats = degree_stats(5, edges)
    workload_score = workload_mismatch_score(topology, workload)

    estimated_freqs = [
        estimate_quarter_wave_frequency_ghz(length, eps_eff=rules.eps_eff)
        for length in lengths
    ]

    return {
        "topology": topology,
        "workload": workload,
        "meander_density": meander_density,
        "n_edges": len(edges),
        "max_degree": stats["max_degree"],
        "total_route_length_mm": total_length,
        "longest_route_mm": longest,
        "crossings": crossings,
        "drc_violations": len(violations),
        "drc_notes": "PASS" if not violations else " | ".join(violations),
        "crosstalk_proxy": xtalk,
        "workload_mismatch": workload_score,
        "min_est_qw_freq_ghz": min(estimated_freqs) if estimated_freqs else 0.0,
        "avg_est_qw_freq_ghz": sum(estimated_freqs) / len(estimated_freqs) if estimated_freqs else 0.0,
    }
