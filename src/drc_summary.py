"""Task 5 — DRC/manufacturability summary.

Creates a rule-level PASS/FAIL table for the final selected layouts.
This is not foundry signoff; it summarizes our self-defined project DRC.
"""

import pandas as pd

from .design_rules import (
    MIN_QUBIT_GAP_MM,
    MIN_CPW_WIDTH_UM,
    MIN_CPW_GAP_UM,
    EDGE_KEEPOUT_MM,
    MIN_ROUTE_SPACING_MM,
)


def build_drc_summary(best_df):
    rows = []

    for row in best_df.itertuples():
        topology = row.topology

        rows.extend(
            [
                {
                    "topology": topology,
                    "rule": "Total DRC violations",
                    "threshold": "must equal 0",
                    "measured_value": int(row.drc_violations),
                    "status": "PASS" if int(row.drc_violations) == 0 else "FAIL",
                    "notes": row.drc_notes,
                },
                {
                    "topology": topology,
                    "rule": "Route crossings",
                    "threshold": "must equal 0 for no crossing airbridges",
                    "measured_value": int(row.crossings),
                    "status": "PASS" if int(row.crossings) == 0 else "FAIL",
                    "notes": "No crossing airbridges required"
                    if int(row.crossings) == 0
                    else "Airbridge/crossover would be required",
                },
                {
                    "topology": topology,
                    "rule": "Minimum CPW envelope route clearance",
                    "threshold": f">= {MIN_ROUTE_SPACING_MM} mm",
                    "measured_value": float(row.min_route_clearance_mm),
                    "status": (
                        "PASS"
                        if float(row.min_route_clearance_mm) >= MIN_ROUTE_SPACING_MM
                        else "FAIL"
                    ),
                    "notes": "Geometry-based crosstalk/manufacturability proxy",
                },
                {
                    "topology": topology,
                    "rule": "Minimum qubit pocket gap",
                    "threshold": f">= {MIN_QUBIT_GAP_MM} mm",
                    "measured_value": "checked by metal_analysis.py",
                    "status": "PASS" if int(row.drc_violations) == 0 else "SEE_NOTES",
                    "notes": "Pocket spacing violations are included in drc_notes if present",
                },
                {
                    "topology": topology,
                    "rule": "CPW trace width/gap",
                    "threshold": f">= {MIN_CPW_WIDTH_UM:.0f}/{MIN_CPW_GAP_UM:.0f} um",
                    "measured_value": "nominal 10/6 um",
                    "status": "PASS" if int(row.drc_violations) == 0 else "SEE_NOTES",
                    "notes": "Actual route options are checked in metal_analysis.py",
                },
                {
                    "topology": topology,
                    "rule": "Chip-edge keepout",
                    "threshold": f">= {EDGE_KEEPOUT_MM} mm",
                    "measured_value": "checked on built geometry",
                    "status": "PASS" if int(row.drc_violations) == 0 else "SEE_NOTES",
                    "notes": "All component geometry must remain inside allowed chip region",
                },
            ]
        )

    return pd.DataFrame(rows)
