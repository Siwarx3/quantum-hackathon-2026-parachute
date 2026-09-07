"""Generate a four-page report from measured sweep data."""
import textwrap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def write_report(root, sweep, best):
    table = best.to_string(index=False)
    winner = best.sort_values('total_route_length_mm').iloc[0].topology if len(best) else 'none'
    sections = [
        ('1. Design, rules and reproducibility',
         'AQH26 Track 4 — Five-qubit hardware layout comparison\n\n'
         'We implement physical planar TransmonPocket qubits and RoutePathfinder CPW couplers in Qiskit Metal. '
         'The primary results below are computed directly from actual Metal route objects with bend corrections, '
         'not qubit-center straight lines. Both candidates use a standardized 12 x 10 mm die, five transmon pockets, '
         'and four CPW couplers. The chain uses opposing adjacent pads; the star uses four distinct hub pads and diagonal leaves.\n\n'
         'Self-defined rules (not a foundry PDK): pocket bounding-box gap >= 0.30 mm; all component '
         'geometry remains 0.50 mm inside chip edges; route CPW width >= 8 um and gap >= 4 um '
         '(nominal 10/6 um); CPW outer-envelope clearance >= 0.15 mm. We check route self/intersections, '
         'pin endpoints, build status and non-endpoint pocket obstruction. Shared-hub routes are checked too. '
         'Fillet clearance is assessed conservatively using unrounded centerlines buffered by CPW envelope.\n\n'
         'Reproduce with python run_all.py. CSV files retain every sweep point and violation. '
         'designs/*.py recreate the selected Metal designs. results/environment.json records versions. '
         'The separate run_proxy.py offers a fast three-topology screening study; its ring and meander '
         'results are estimates and are excluded from this physical comparison.'),
        ('2. Optimization and measured comparison',
         'Objective: minimize total built CPW route length and longest individual route subject to zero DRC violations. '
         'Invalid candidates cannot win through a soft penalty. We sweep across both coarse and fine boundary grids '
         '(0.9–2.8 mm) for each topology. The chain variable is neighbor pitch; the star variable is hub-to-leaf radius. '
         'All candidates use the same die, transmon dimensions and CPW rules.\n\n'
         + '\n'.join(f'{r.topology}: optimal parameter {getattr(r, "layout_parameter_mm", getattr(r, "pitch_mm", 0.0)):.2f} mm; total {r.total_route_length_mm:.3f} mm; '
                      f'longest {r.longest_route_mm:.3f} mm; opt. cost {getattr(r, "optimization_cost_mm", getattr(r, "optimization_cost", 0.0)):.3f}; '
                      f'crossings {int(r.crossings)}; DRC {int(r.drc_violations)}.' for r in best.itertuples())
         + '\n\nPlot: left, built routing objective and cost; right, rule failures across the sweep. '
         'Zero crossings means these layouts need no crossing airbridges; ground-plane stitching '
         'requirements require a separate microwave design review.'),
        ('3. Workload and EM trade-offs',
         'Chain: a natural match to nearest-neighbor Trotter/chain interactions, maximum degree 2, '
         'graph diameter 4. Star: native hub-to-leaf interactions, maximum degree 4, diameter 2. '
         'A fixed hub-control GHZ circuit has four native star CNOTs, but a chain can also prepare '
         'GHZ with four CNOTs by propagating entanglement. Shared-hub gates serialize; star topology '
         'alone does not prove faster GHZ. Circuit compilation and gate calibration are future validation.\n\n'
         'Length is a geometric exposure proxy, not a prediction of T1/T2, fidelity or loss. '
         'A uniform transmission line gives f_quarter = c/(4 L sqrt(eps_eff)), or '
         'f_half = c/(2 L sqrt(eps_eff)); epsilon_eff=6 is only a screening assumption. '
         'The actual boundary conditions and capacitive loading determine which model applies. '
         'These short routed couplers are not frequency-tuned resonators. A 6 GHz illustrative '
         'quarter-wave line would be about 5.10 mm, and a half-wave line about 10.20 mm. '
         'Meanders would require actual geometry, bend/spacing checks and re-optimization.\n\n'
         'Close parallel CPW segments can enhance unwanted coupling. We report minimum envelope '
         'separation, not measured crosstalk; the four-pad hub also concentrates capacitance and '
         'frequency-collision risk. Full EM extraction, junction parameters, readout/feedlines, '
         'packaging, ground continuity and fabrication PDK checks are not included.'),
        ('4. Recommendation and iteration evidence',
         f'The lowest-cost feasible candidate in this sweep is {winner}. For a nearest-neighbor '
         'demonstrator we recommend the chain as the next fabrication-development candidate because '
         'its degree-two wiring is simple and directly supports the workload. For fixed central-control '
         'interactions choose the star, accepting hub loading and serialization. This is a recommendation '
         'for further engineering; neither layout is fabrication-ready without EM and process validation.\n\n'
         'Iteration record:\n'
         '1. Original chain pins faced away from neighbors; a 1.5 mm probe produced detours and fillet warnings. '
         'Changed to facing pads and 100 um leads.\n'
         '2. Original builders used different chip footprints; standardized both to 12 x 10 mm.\n'
         '3. Original totals read requested total_length; replaced with route.length, including Metal corner correction.\n'
         '4. Proxy optimizer used a soft DRC penalty; restricted selection to feasible rows.\n'
         '5. Original edge checks covered only qubits; extended checks to all built geometry.\n'
         '6. Proxy crossing logic skips shared qubits; physical checks compare every route pair.\n'
         f'7. Actual sweep recorded {int((sweep.drc_violations > 0).sum())} rejected candidates of {len(sweep)}; '
         'see metal_sweep.csv for exact violations and successful revised spacings.\n\n'
         'SDG 9: reproducible hardware design and infrastructure skills. SDG 4: transparent integration, '
         'measured iteration and explicit modeling limits make the workflow reusable for education. '
         'Source of requirements: supplied Quantum hardware problem.pdf, Track 4. Existing Task reports '
         'are retained as historical material; this report and the generated CSVs describe the integrated run.')]
    (root/'reports/technical_report.md').write_text('\n\n'.join('# '+title+'\n\n'+body for title,body in sections)+'\n')
    with PdfPages(root/'reports/technical_report.pdf') as pdf:
        for i,(title,body) in enumerate(sections):
            fig = plt.figure(figsize=(8.27,11.69))
            fig.text(.08,.95,title,fontsize=16,weight='bold',va='top')
            wrapped = '\n\n'.join('\n'.join(textwrap.wrap(p,96)) for p in body.split('\n\n'))
            fig.text(.08,.90,wrapped,fontsize=10,va='top',linespacing=1.5)
            if i == 1:
                ax = fig.add_axes([.08,.40,.84,.10]); ax.axis('off')
                cells = [[r.topology, f'{r.total_route_length_mm:.3f}', f'{r.longest_route_mm:.3f}', str(int(r.crossings)), str(int(r.drc_violations))] for r in best.itertuples()]
                tab = ax.table(cellText=cells, colLabels=['Topology','Total mm','Longest mm','Crossings','DRC'],loc='center')
                tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1,1.5)
            if i == 0 and (root/'figures/metal_linear.png').exists():
                ax = fig.add_axes([.08,.055,.84,.29]); ax.imshow(plt.imread(root/'figures/metal_linear.png')); ax.axis('off')
            if i in (1,2):
                path = root/('figures/metal_sweep.png' if i == 1 else 'figures/metal_star.png')
                if path.exists():
                    ax = fig.add_axes([.08,.055,.84,.32 if i == 1 else .29]); ax.imshow(plt.imread(path)); ax.axis('off')
            fig.text(.5,.025,f'{i+1} / 4',ha='center',fontsize=9)
            pdf.savefig(fig); plt.close(fig)
