# Judge discussion notes

**What did you optimize?**
Total CPW length measured from built Metal routes, under hard geometry constraints.
We retain longest route, crossings and clearance as separate comparison metrics.
The physical sweep varies seven spacings for each of two topologies on the same die.

**Why these topologies?**
A chain directly represents nearest-neighbor interactions and limits node degree.
A star directly represents hub-to-leaf interactions. The star's connectivity reduces
some interaction distances, but hub gates cannot all run simultaneously.

**Does the star always prepare GHZ faster?**
No. Both connected layouts support four entangling gates for a five-qubit GHZ state
with a suitable construction. Fixed hub-control circuits favor star connectivity;
actual depth depends on the construction, mapping, scheduling and calibrated gates.
The imported workload score describes a fixed interaction graph, not optimal GHZ synthesis.

**Why did the optimum move toward smaller spacing?**
The objective rewards shorter routes. Without a frequency target, a shortest-route
optimum near the feasible spacing boundary is expected. We show rejected spacings
and do not claim this sweep solves frequency allocation or resonator synthesis.

**Are the frequency and coherence numbers measured?**
No. The physical results are geometry measurements. Transmission-line estimates
are illustrative; boundary conditions, loading and effective permittivity must be
validated. We do not infer T1, T2 or fidelity from a route length.

**What is your strongest improvement over the original baseline?**
Facing chain pads remove unnecessary detours. The integration measures built routes,
checks all geometry against edge keepouts, checks every pair of routes including
shared-hub routes, and prevents a DRC-violating candidate from winning.

**Is this ready to fabricate?**
It is a reproducible layout study with self-defined checks. Next steps are adding
readout and control structures, setting junction and resonator targets, extracting
coupling/loss with EM tools, checking the actual process PDK and reviewing packaging.

**What would you fabricate first?**
Recommend the Linear Chain as the first fabrication-development candidate under our route-length,
clearance, and DRC metrics (shortest 1.400 mm routing, largest 0.828 mm clearance, 0 crossings).
The Star topology remains preferred for experiments dominated by fixed hub-to-leaf interactions,
accepting central hub capacitive density and gate serialization. Refer to `results/task6_synthesis.csv`
and `reports/task6_recommendation.md` for the complete side-by-side synthesis.

**How did you evaluate EM routing, crossings, and airbridges (Task 4)?**
Both topologies achieve 0 crossings and require 0 crossing airbridges, enabling single-layer
planar lithography. We assess geometric clearance by buffering the physical CPW envelope
(10 um center conductor + 6 um ground etch = 22 um outer envelope) rather than 1D mathematical
centerlines. Linear achieves 0.828 mm clearance (low crosstalk risk proxy); Star achieves 0.368 mm
clearance (both pass the >= 0.15 mm DRC rule). For microwave scale comparison, an illustrative
6 GHz quarter-wave resonator on silicon (eps_eff=6.0) requires ~5.10 mm (half-wave ~10.20 mm);
our couplers are short direct interconnects (0.350 mm and 0.839 mm) rather than meandering resonators.
See `results/em_routing_summary.csv`.

**What failures occurred during layout iteration and how were they resolved (Task 5)?**
Real hardware design is iterative. Across the 14-point sweep, 4 candidates failed:
1. Linear at 0.9 mm: Pocket-to-pocket gap was 0.00 mm (colliding pockets < 0.3 mm threshold). Resolved by shifting pitch to >= 1.2 mm.
2. Star at 0.9 mm: Pocket-to-pocket gap was -0.10 mm (severe overlapping leaf pockets). Resolved by increasing radius to >= 1.5 mm.
3. Star at 1.2 mm: Pocket-to-pocket gap was 0.17 mm (< 0.3 mm threshold). Resolved by increasing radius to >= 1.5 mm.
4. Linear at 2.8 mm: Outer qubit pocket reached within 0.10 mm of the chip edge (< 0.5 mm keep-out). Resolved by constraining sweep within the feasible 1.2-2.5 mm envelope.
All 6 final design rules pass with zero violations for the selected designs. See `results/drc_summary.csv` and `results/drc_iteration_failures.csv`.

**Where is the complete evidence?**
The full evidence is captured across Tasks 1 to 6 in:
- `results/metal_sweep.csv` & `results/metal_comparison.csv` (Task 3 physical optimization)
- `results/em_routing_summary.csv` (Task 4 EM-aware routing & clearance)
- `results/drc_summary.csv` & `results/drc_iteration_failures.csv` (Task 5 manufacturability & iteration history)
- `results/task6_synthesis.csv` & `reports/task6_recommendation.md` (Task 6 comparative synthesis)
- `reports/technical_report.pdf` (formal 4-page submission report)
- `figures/metal_linear.png`, `figures/metal_star.png`, `figures/metal_sweep.png` (high-res geometry renders)

