"""Central baseline design rules for AQH26 Track 4.

These values are self-defined project assumptions used consistently
for comparing our chip candidates. They are NOT claimed to be a
specific commercial foundry PDK.
"""
from dataclasses import dataclass, asdict

# ------------------------------------------------------------
# CHIP DIMENSIONS
# ------------------------------------------------------------

CHIP_SIZE_X = "12mm"
CHIP_SIZE_Y = "10mm"
CHIP_WIDTH_MM = 12.0
CHIP_HEIGHT_MM = 10.0

# ------------------------------------------------------------
# BASELINE QUBIT PLACEMENT
# ------------------------------------------------------------

BASELINE_PITCH_MM = 2.5

# Minimum allowed edge-to-edge distance between qubit pocket cutouts.
MIN_QUBIT_GAP_MM = 0.30

# ------------------------------------------------------------
# CPW GEOMETRY
# ------------------------------------------------------------

# Geometry actually used in our baseline design (targeting ~50 Ohm).
CPW_WIDTH = "10um"
CPW_GAP = "6um"
CPW_WIDTH_MM = 0.010
CPW_GAP_MM = 0.006

# Minimum geometry accepted by our self-defined DRC.
MIN_CPW_WIDTH_MM = 0.008    # 8 µm
MIN_CPW_GAP_MM = 0.004      # 4 µm
MIN_CPW_WIDTH_UM = 8.0
MIN_CPW_GAP_UM = 4.0

# ------------------------------------------------------------
# CHIP EDGE AND ROUTE CLEARANCE
# ------------------------------------------------------------

EDGE_KEEPOUT_MM = 0.50
MIN_ROUTE_SPACING_MM = 0.15

# Effective dielectric constant (silicon substrate ~11.45, air ~1.0)
EPS_EFF = 6.0


@dataclass(frozen=True)
class DesignRules:
    """Baseline comparative design rules used for screening and optimization."""

    chip_width_mm: float = CHIP_WIDTH_MM
    chip_height_mm: float = CHIP_HEIGHT_MM

    edge_keepout_mm: float = EDGE_KEEPOUT_MM
    min_qubit_spacing_mm: float = 1.00  # Screening center-to-center proxy

    cpw_width_um: float = 10.0
    min_cpw_width_um: float = MIN_CPW_WIDTH_UM

    cpw_gap_um: float = 6.0
    min_cpw_gap_um: float = MIN_CPW_GAP_UM

    min_route_spacing_mm: float = MIN_ROUTE_SPACING_MM
    eps_eff: float = EPS_EFF

    def to_dict(self):
        return asdict(self)
