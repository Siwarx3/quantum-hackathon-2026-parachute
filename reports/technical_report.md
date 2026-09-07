# 1. Design, rules and reproducibility

AQH26 Track 4 — Five-qubit hardware layout comparison

We implement physical planar TransmonPocket qubits and RoutePathfinder CPW couplers in Qiskit Metal. The primary results below are computed directly from actual Metal route objects with bend corrections, not qubit-center straight lines. Both candidates use a standardized 12 x 10 mm die, five transmon pockets, and four CPW couplers. The chain uses opposing adjacent pads; the star uses four distinct hub pads and diagonal leaves.

Self-defined rules (not a foundry PDK): pocket bounding-box gap >= 0.30 mm; all component geometry remains 0.50 mm inside chip edges; route CPW width >= 8 um and gap >= 4 um (nominal 10/6 um); CPW outer-envelope clearance >= 0.15 mm. We check route self/intersections, pin endpoints, build status and non-endpoint pocket obstruction. Shared-hub routes are checked too. Fillet clearance is assessed conservatively using unrounded centerlines buffered by CPW envelope.

Reproduce with python run_all.py. CSV files retain every sweep point and violation. designs/*.py recreate the selected Metal designs. results/environment.json records versions. The separate run_proxy.py offers a fast three-topology screening study; its ring and meander results are estimates and are excluded from this physical comparison.

# 2. Optimization and measured comparison

Objective: minimize total built CPW route length and longest individual route subject to zero DRC violations. Invalid candidates cannot win through a soft penalty. We sweep across both coarse and fine boundary grids (0.9–2.8 mm) for each topology. The chain variable is neighbor pitch; the star variable is hub-to-leaf radius. All candidates use the same die, transmon dimensions and CPW rules.

linear: optimal parameter 1.20 mm; total 1.400 mm; longest 0.350 mm; opt. cost 1.400; crossings 0; DRC 0.
star: optimal parameter 1.50 mm; total 3.356 mm; longest 0.839 mm; opt. cost 3.356; crossings 0; DRC 0.

Plot: left, built routing objective and cost; right, rule failures across the sweep. Zero crossings means these layouts need no crossing airbridges; ground-plane stitching requirements require a separate microwave design review.

# 3. Workload and EM trade-offs

Chain: a natural match to nearest-neighbor Trotter/chain interactions, maximum degree 2, graph diameter 4. Star: native hub-to-leaf interactions, maximum degree 4, diameter 2. A fixed hub-control GHZ circuit has four native star CNOTs, but a chain can also prepare GHZ with four CNOTs by propagating entanglement. Shared-hub gates serialize; star topology alone does not prove faster GHZ. Circuit compilation and gate calibration are future validation.

Length is a geometric exposure proxy, not a prediction of T1/T2, fidelity or loss. A uniform transmission line gives f_quarter = c/(4 L sqrt(eps_eff)), or f_half = c/(2 L sqrt(eps_eff)); epsilon_eff=6 is only a screening assumption. The actual boundary conditions and capacitive loading determine which model applies. These short routed couplers are not frequency-tuned resonators. A 6 GHz illustrative quarter-wave line would be about 5.10 mm, and a half-wave line about 10.20 mm. Meanders would require actual geometry, bend/spacing checks and re-optimization.

Close parallel CPW segments can enhance unwanted coupling. We report minimum envelope separation, not measured crosstalk; the four-pad hub also concentrates capacitance and frequency-collision risk. Full EM extraction, junction parameters, readout/feedlines, packaging, ground continuity and fabrication PDK checks are not included.

# 4. Recommendation and iteration evidence

The lowest-cost feasible candidate in this sweep is linear. For a nearest-neighbor demonstrator we recommend the chain as the next fabrication-development candidate because its degree-two wiring is simple and directly supports the workload. For fixed central-control interactions choose the star, accepting hub loading and serialization. This is a recommendation for further engineering; neither layout is fabrication-ready without EM and process validation.

Iteration record:
1. Original chain pins faced away from neighbors; a 1.5 mm probe produced detours and fillet warnings. Changed to facing pads and 100 um leads.
2. Original builders used different chip footprints; standardized both to 12 x 10 mm.
3. Original totals read requested total_length; replaced with route.length, including Metal corner correction.
4. Proxy optimizer used a soft DRC penalty; restricted selection to feasible rows.
5. Original edge checks covered only qubits; extended checks to all built geometry.
6. Proxy crossing logic skips shared qubits; physical checks compare every route pair.
7. Actual sweep recorded 4 rejected candidates of 14; see metal_sweep.csv for exact violations and successful revised spacings.

SDG 9: reproducible hardware design and infrastructure skills. SDG 4: transparent integration, measured iteration and explicit modeling limits make the workflow reusable for education. Source of requirements: supplied Quantum hardware problem.pdf, Track 4. Existing Task reports are retained as historical material; this report and the generated CSVs describe the integrated run.
