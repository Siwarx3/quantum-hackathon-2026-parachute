"""Track 4 - Star topology, 5 qubits, with routed couplers."""
from qiskit_metal import designs, Dict
import qiskit_metal as qm
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder
import math

# Corner keys: each pad lives on one of the 4 corners of the pocket (loc_W, loc_H in {-1,1})
CORNERS = {
    'ne': (1, 1), 'nw': (-1, 1), 'se': (1, -1), 'sw': (-1, -1),
}
OPPOSITE = {'ne': 'sw', 'nw': 'se', 'se': 'nw', 'sw': 'ne'}

def build_star(radius_mm=2.5):
    design = designs.DesignPlanar()
    design.chips.main.size.size_x = '10mm'
    design.chips.main.size.size_y = '10mm'

    TransmonPocket(design, 'Q1', options=Dict(
        pos_x='0mm', pos_y='0mm', pad_width='425um', pocket_height='650um',
        connection_pads=Dict(**{k: Dict(loc_W=w, loc_H=h) for k, (w, h) in CORNERS.items()}),
    ))

    # Place outer qubits diagonally (45, 135, 225, 315 deg) so a corner pad naturally points at Q1
    outer_dirs = ['ne', 'nw', 'sw', 'se']
    angle_map = {'ne': math.pi/4, 'nw': 3*math.pi/4, 'sw': 5*math.pi/4, 'se': 7*math.pi/4}

    for i, d in enumerate(outer_dirs, start=2):
        angle = angle_map[d]
        x, y = radius_mm * math.cos(angle), radius_mm * math.sin(angle)
        pad_dir = OPPOSITE[d]  # pad faces back toward center
        w, h = CORNERS[pad_dir]
        TransmonPocket(design, f'Q{i}', options=Dict(
            pos_x=f'{x:.3f}mm', pos_y=f'{y:.3f}mm',
            pad_width='425um', pocket_height='650um',
            connection_pads=Dict(p=Dict(loc_W=w, loc_H=h)),
        ))

    design.rebuild()

    routes = {}
    for i, d in zip(range(2, 6), outer_dirs):
        rname = f'route_Q1_Q{i}'
        routes[rname] = RoutePathfinder(design, rname, options=Dict(
            pin_inputs=Dict(start_pin=Dict(component='Q1', pin=d),
                             end_pin=Dict(component=f'Q{i}', pin='p')),
            fillet='50um',
        ))
    design.rebuild()
    return design, routes

if __name__ == '__main__':
    design, routes = build_star(radius_mm=2.5)
    fig = qm.view(design)
    fig.savefig('star_render.png', dpi=150)
    total_len_mm = sum(float(design.components[r].options.total_length.strip('mm'))
                        for r in routes)
    print("Per-coupler lengths (mm):",
          {r: design.components[r].options.total_length for r in routes})
    print("Total routing length (mm):", total_len_mm)
