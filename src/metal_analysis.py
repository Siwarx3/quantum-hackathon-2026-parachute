"""Geometry checks on built Metal components; not foundry or EM signoff."""
from itertools import combinations
import math
from shapely.geometry import box, Point
from .drc_check import check_qubit_spacing
from .design_rules import (
    CHIP_WIDTH_MM,
    CHIP_HEIGHT_MM,
    EDGE_KEEPOUT_MM,
    MIN_QUBIT_GAP_MM,
    MIN_CPW_WIDTH_MM,
    MIN_CPW_GAP_MM,
    MIN_ROUTE_SPACING_MM,
)


def analyze(design, routes):
    notes = []
    paths = design.qgeometry.tables['path']
    traces = {}
    envelopes = {}
    lengths = []
    x_bound = CHIP_WIDTH_MM / 2.0 - EDGE_KEEPOUT_MM
    y_bound = CHIP_HEIGHT_MM / 2.0 - EDGE_KEEPOUT_MM
    allowed = box(-x_bound, -y_bound, x_bound, y_bound)
    for name, component in design.components.items():
        if component.status != 'good':
            notes.append(f'{name}: build status {component.status}')
        for kind in ('poly', 'path', 'junction'):
            table = design.qgeometry.tables[kind]
            for _, row in table[table.component == component.id].iterrows():
                geom = row.geometry
                if kind != 'poly':
                    geom = geom.buffer(float(row.width)/2)
                if not allowed.covers(geom):
                    notes.append(f'{name}/{row["name"]}: edge keepout')
    for name, route in routes.items():
        rows = paths[(paths.component == route.id) & (paths.name == 'trace')]
        if len(rows) != 1:
            notes.append(f'{name}: missing or ambiguous trace')
            continue
        row = rows.iloc[0]
        line = row.geometry
        traces[name] = line
        width = float(design.parse_value(route.options.trace_width))
        gap = float(design.parse_value(route.options.trace_gap))
        if width < MIN_CPW_WIDTH_MM - 1e-10 or gap < MIN_CPW_GAP_MM - 1e-10:
            notes.append(f'{name}: CPW below {MIN_CPW_WIDTH_MM*1e3:.0f}um/{MIN_CPW_GAP_MM*1e3:.0f}um minimum')
        envelopes[name] = line.buffer(width/2 + gap)
        lengths.append(float(route.length))
        if not line.is_simple:
            notes.append(f'{name}: self intersection')
        for endpoint, coord in zip(('start_pin', 'end_pin'), (line.coords[0], line.coords[-1])):
            pin = route.options.pin_inputs[endpoint]
            target = design.components[pin.component].pins[pin.pin].middle
            if Point(coord).distance(Point(target)) > 1e-7:
                notes.append(f'{name}: disconnected {endpoint}')
        attached = {route.options.pin_inputs[k].component for k in ('start_pin', 'end_pin')}
        for qname, qubit in design.components.items():
            if qname.startswith('Q') and qname not in attached:
                if envelopes[name].intersects(box(*qubit.qgeometry_bounds())):
                    notes.append(f'{name}: intersects non-endpoint {qname} pocket')
    crossings = 0
    separations = []
    for a, b in combinations(traces, 2):
        if traces[a].intersects(traces[b]):
            crossings += 1
            notes.append(f'{a}/{b}: intersection')
        sep = envelopes[a].distance(envelopes[b])
        separations.append(sep)
        if sep < MIN_ROUTE_SPACING_MM - 1e-9:
            notes.append(f'{a}/{b}: CPW envelope clearance {sep:.4f}mm < {MIN_ROUTE_SPACING_MM}mm')
    for a,b,gap in check_qubit_spacing(design, MIN_QUBIT_GAP_MM):
        notes.append(f'{a}/{b}: pocket gap {gap}mm < {MIN_QUBIT_GAP_MM}mm')
    expected_routes = len(routes)
    if len(lengths) != expected_routes:
        notes.append(f'Expected {expected_routes} complete routes, found {len(lengths)}')
    return dict(total_route_length_mm=sum(lengths), longest_route_mm=max(lengths, default=0),
                crossings=crossings, min_route_clearance_mm=min(separations, default=0),
                drc_violations=len(notes), drc_notes=' | '.join(notes) or 'PASS')


def render(design, output, title):
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle
    fig, ax = plt.subplots(figsize=(9, 6))
    for kind in ('poly','path','junction'):
        for _, row in design.qgeometry.tables[kind].sort_values('subtract', ascending=False).iterrows():
            geom = row.geometry
            color = '#dce7ee' if row.get('subtract', False) else '#155e75'
            if kind == 'poly':
                for poly in getattr(geom, 'geoms', [geom]):
                    ax.add_patch(Polygon(list(poly.exterior.coords), color=color))
            else:
                ax.plot(*geom.xy, color=color, linewidth=1 if kind == 'junction' else 2)
    ax.add_patch(Rectangle((-6,-5),12,10,fill=False))
    ax.add_patch(Rectangle((-5.5,-4.5),11,9,fill=False,linestyle='--',edgecolor='orange'))
    for name, comp in design.components.items():
        if name.startswith('Q'):
            ax.text(float(comp.p.pos_x), float(comp.p.pos_y)+.5, name, ha='center')
    ax.set(xlim=(-6.2,6.2),ylim=(-5.2,5.2),xlabel='x (mm)',ylabel='y (mm)',title=title,aspect='equal')
    fig.tight_layout(); fig.savefig(output,dpi=180); plt.close(fig)
