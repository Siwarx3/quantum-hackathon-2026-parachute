from drc_check import run_all_checks
from chain_topology import build_chain
from star_topology import build_star

# these tests should passes because they meet the baseline
design, routes = build_chain(pitch_mm=2.5)
run_all_checks(design)

design2, routes2 = build_star(radius_mm=2.5)
run_all_checks(design2)

# tighten/loosen the rules to test edge cases:
"--- Sensitivity test: stricter keep-out ---"
run_all_checks(design, min_qubit_gap_mm=0.5, keepout_margin_mm=1.0)