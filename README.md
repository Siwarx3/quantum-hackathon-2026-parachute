# Alexandria Quantum Hackathon 2026 — Track 4: Qiskit Metal / Quantum Hardware Design

5-qubit superconducting chip layout optimization using Qiskit Metal (now Quantum Metal).
Compares linear chain and star coupling-map topologies against qubit placement, routing,
and design-rule (DRC) constraints.

## Team

- [Siwar Diab] — computer engineering, Qiskit Metal setup + baseline design + DRC
- [Teammate] — [background] — [role]
- [Teammate] — [background] — [role]
- [Teammate] — [background] — [role]
- [Teammate] — [background] — [role]

## Setup

```bash
pip install "quantum-metal"
```

Do **not** additionally `pip install qiskit` into this same environment — it upgrades
numpy to a version quantum-metal doesn't support. Use a separate environment if you need
full Qiskit (e.g. for `CouplingMap`); this repo's graph metrics use `networkx` instead.

## Repo structure

```
src/        Python scripts (topology builds, DRC checks, sweeps, graph metrics)
renders/    PNG outputs of each chip layout
reports/    Task write-ups (.docx)
README.md   This file
```

## Running

```bash
cd src
python chain_topology.py   # builds + renders the linear chain topology
python star_topology.py    # builds + renders the star topology
python drc_check.py        # runs design rule checks against both baselines
python sweep.py            # parameter sweep: spacing vs. total routing length
python topology_graphs.py  # graph-theoretic comparison (degree, diameter, path length)
```

## Task status

- [x] Task 1 — Baseline chip design + design rules (see `reports/Task1_Report.docx`)
- [x] Task 2 — Coupling map / topology exploration
- [ ] Task 3 — Physical layout optimization (sweep in progress)
- [ ] Task 4 — EM-aware routing considerations
- [ ] Task 5 — Design rule / manufacturability check
- [ ] Task 6 — Comparative analysis
