# Integration provenance

Source companion checkout: `/home/lu/Documents/Alexu/AQH26/AQH/parachuteAQH26`
at commit `e65eb14d9df60687b5f628d44d03673b922210c5`.
Imported `src/{__init__,design_rules,geometry_metrics,optimizer,plotting,topologies}.py`
and `run_all.py` (renamed `run_proxy.py`). Original contributors retain attribution.
The source checkout was read/copied only, not modified.

Adaptations: shared 12 x 10 mm chip dimensions, diagonal proxy star matching the
physical orientation, and hard feasibility filtering in candidate selection.
Synthetic meander results and centerline estimates remain screening-only.

The current repository contributes original TransmonPocket builders and baseline
DRC. Integration fixes the chain's pin direction, provides longer route leads,
measures built route lengths, adds geometry-level checks and generates submission
artifacts directly from the physical sweep.

Source challenge: Track 4 — Qiskit Metal / Quantum Hardware Design Workflow (Alexandria Quantum Hackathon 2026).
The challenge's six tasks and deliverables guided the engineering implementation.
