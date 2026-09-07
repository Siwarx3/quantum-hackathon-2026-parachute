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
Develop the chain for a nearest-neighbor demonstrator, subject to those checks.
Use the star if central-control interactions are the main requirement. Refer to
metal_comparison.csv for the actual length trade-off; do not substitute proxy scores.

**Where is the evidence?**
The four-page report explains the method. metal_sweep.csv records all 14 trials,
metal_comparison.csv identifies feasible selections, figures/metal_*.png shows
built geometry and the sweep, and designs/*.py reconstructs the selected designs.
