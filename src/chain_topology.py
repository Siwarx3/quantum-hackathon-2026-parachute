"""Track 4 - Linear Chain topology, 5 qubits, with routed couplers."""
from qiskit_metal import designs, Dict
import qiskit_metal as qm
from qiskit_metal.qlibrary.qubits.transmon_pocket import TransmonPocket
from qiskit_metal.qlibrary.tlines.pathfinder import RoutePathfinder

def build_chain(pitch_mm=2.5):
    design = designs.DesignPlanar()
    design.chips.main.size.size_x = '12mm'
    design.chips.main.size.size_y = '6mm'

    positions = [(-2*pitch_mm, 0), (-pitch_mm, 0), (0, 0), (pitch_mm, 0), (2*pitch_mm, 0)]
    for i, (x, y) in enumerate(positions, start=1):
        TransmonPocket(design, f'Q{i}', options=Dict(
            pos_x=f'{x}mm', pos_y=f'{y}mm',
            pad_width='425um', pocket_height='650um',
            connection_pads=Dict(a=Dict(loc_W=1, loc_H=1), b=Dict(loc_W=-1, loc_H=1)),
        ))

    design.rebuild()

    routes = {}
    for i in range(1, 5):
        src, dst = f'Q{i}', f'Q{i+1}'
        rname = f'route_{src}_{dst}'
        routes[rname] = RoutePathfinder(design, rname, options=Dict(
            pin_inputs=Dict(start_pin=Dict(component=src, pin='b'),
                             end_pin=Dict(component=dst, pin='a')),
            fillet='50um',   # smaller fillet -> fewer geometry warnings
        ))
    design.rebuild()
    return design, routes

if __name__ == '__main__':
    design, routes = build_chain(pitch_mm=2.5)
    fig = qm.view(design)
    fig.savefig('chain_render.png', dpi=150)

    total_len_mm = sum(float(design.components[r].options.total_length.strip('mm'))
                        for r in routes)
    print("Per-coupler lengths (mm):",
          {r: design.components[r].options.total_length for r in routes})
    print("Total routing length (mm):", total_len_mm)
