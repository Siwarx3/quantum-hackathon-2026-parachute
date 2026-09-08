"""Task 4 — EM-aware routing summary.

This module converts physical routing metrics into clear EM-aware interpretations.
It does not claim full-wave HFSS/Ansys simulation.
"""
import math
import pandas as pd
from .design_rules import EPS_EFF, MIN_ROUTE_SPACING_MM


def quarter_wave_length_mm(freq_ghz=6.0, eps_eff=EPS_EFF):
    """Approximate λ/4 resonator length in mm.
    f ≈ c / (4 L sqrt(eps_eff)) so L ≈ c / (4 f sqrt(eps_eff)).
    """
    c = 299_792_458.0
    freq_hz = freq_ghz * 1e9
    return c / (4.0 * freq_hz * math.sqrt(eps_eff)) * 1e3


def half_wave_length_mm(freq_ghz=6.0, eps_eff=EPS_EFF):
    """Approximate λ/2 resonator length in mm."""
    c = 299_792_458.0
    freq_hz = freq_ghz * 1e9
    return c / (2.0 * freq_hz * math.sqrt(eps_eff)) * 1e3


def equivalent_quarter_wave_frequency_ghz(length_mm, eps_eff=EPS_EFF):
    """Equivalent λ/4 frequency for a given route length.

    This is only an illustrative EM proxy. The routed couplers in this project
    are not claimed to be frequency-tuned resonators.
    """
    if length_mm <= 0 or math.isnan(length_mm):
        return float("nan")
    c = 299_792_458.0
    length_m = length_mm * 1e-3
    return c / (4.0 * length_m * math.sqrt(eps_eff)) / 1e9


def classify_crosstalk_risk(topology, min_clearance_mm):
    """Qualitative crosstalk-risk label from route clearance and topology."""
    if math.isnan(min_clearance_mm):
        return "unknown"
    if min_clearance_mm < MIN_ROUTE_SPACING_MM:
        return "fails route-clearance rule"
    if min_clearance_mm < 3.0 * MIN_ROUTE_SPACING_MM:
        return "watch: close-route geometric crosstalk risk"
    if topology == "star":
        return "moderate: hub capacitance/loading concentration"
    return "lower: distributed local routing"


def build_em_routing_summary(best_df, target_freq_ghz=6.0):
    """Build a Task-4 summary from selected best candidates."""
    qwave_6ghz = quarter_wave_length_mm(target_freq_ghz)
    hwave_6ghz = half_wave_length_mm(target_freq_ghz)
    rows = []
    for row in best_df.itertuples():
        topology = row.topology
        crossings = int(row.crossings)
        min_clearance = float(row.min_route_clearance_mm)
        longest = float(row.longest_route_mm)

        rows.append(
            {
                "topology": topology,
                "total_route_length_mm": float(row.total_route_length_mm),
                "longest_route_mm": longest,
                "crossings": crossings,
                "crossing_airbridges_needed": crossings,
                "min_route_clearance_mm": min_clearance,
                "route_clearance_rule_mm": MIN_ROUTE_SPACING_MM,
                "route_clearance_status": (
                    "PASS" if min_clearance >= MIN_ROUTE_SPACING_MM else "FAIL"
                ),
                "crosstalk_risk_proxy": classify_crosstalk_risk(topology, min_clearance),
                "equivalent_quarter_wave_freq_from_longest_route_ghz": (
                    equivalent_quarter_wave_frequency_ghz(longest)
                ),
                "target_frequency_ghz": target_freq_ghz,
                "approx_6ghz_quarter_wave_length_mm": qwave_6ghz,
                "approx_6ghz_half_wave_length_mm": hwave_6ghz,
                "resonator_interpretation": (
                    "Routed couplers are much shorter than an illustrative 6 GHz "
                    "quarter-wave resonator; they are not claimed as frequency-tuned resonators."
                ),
                "airbridge_interpretation": (
                    "No crossing airbridge needed"
                    if crossings == 0
                    else "Crossing airbridge/crossover would be required"
                ),
            }
        )
    return pd.DataFrame(rows)
