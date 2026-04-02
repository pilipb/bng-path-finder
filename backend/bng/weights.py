# Biodiversity Metric 4.0 distinctiveness scores and road-build costs
# Higher cost = more BNG units lost if road built here = avoid

BNG_WEIGHTS: dict[str, int] = {
    # Distinctiveness 8 — Very High
    "Blanket bog": 8,
    "Lowland raised bog": 8,
    "Upland heath": 8,
    "Upland heathland": 8,
    "Lowland heathland": 8,
    "Ancient semi-natural woodland": 8,
    "Limestone pavement": 8,
    "Limestone pavements": 8,
    "Coastal saltmarsh": 8,
    "Intertidal mudflat": 8,
    "Upland calcareous grassland": 8,
    "Lowland calcareous grassland": 8,
    "Calaminarian grassland": 8,
    "Mountain heaths and willow scrub": 8,
    "Saline lagoons": 8,
    # Distinctiveness 6 — High
    "Lowland meadow": 6,
    "Lowland meadows": 6,
    "Upland hay meadow": 6,
    "Upland hay meadows": 6,
    "Neutral grassland": 6,
    "Upland mixed ash woodland": 6,
    "Traditional orchard": 6,
    "Traditional orchards": 6,
    "Fen": 6,
    "Fens": 6,
    "Reedbed": 6,
    "Reedbeds": 6,
    "Purple moor-grass and rush pasture": 6,
    "Purple moor-grass and rush pastures": 6,
    "Lowland dry acid grassland": 6,
    "Upland acid grassland": 6,
    "Floodplain grazing marsh": 6,
    "Coastal and floodplain grazing marsh": 6,
    "Deciduous woodland": 6,
    # Distinctiveness 4 — Medium
    "Woodland and scrub": 4,
    "Hedgerow": 4,
    "Pond": 4,
    "River or stream": 4,
    "Semi-improved grassland": 4,
    "Wet modified grassland": 4,
    "Broadleaved mixed and yew woodland": 4,
    "Coniferous woodland": 4,
    # Distinctiveness 2 — Low
    "Improved grassland": 2,
    "Modified grassland": 2,
    "Urban green infrastructure": 2,
    "Amenity grassland": 2,
    # Distinctiveness 0 — Very Low / Degraded
    "Bare ground": 0,
    "Sealed surface": 0,
    "Built": 0,
    "Artificial": 0,
}

# Default for unknown/unclassified habitat
DEFAULT_DISTINCTIVENESS = 2

# ── A* pathfinding cost per distinctiveness band ───────────────────────────
# Higher cost → A* steers away from this habitat.
# Distinctiveness 0 uses 1.0 (not 0) so the router can still cross if needed.
DISTINCTIVENESS_COST: dict[int, float] = {
    8: 8.0,
    6: 6.0,
    4: 4.0,
    2: 2.0,
    0: 1.0,
}

# ── DEFRA Statutory Biodiversity Metric 4.0 unit values ───────────────────
# Biodiversity units = area (ha) × distinctiveness × condition × strat. sig.
# Very-low/sealed surfaces score 0 units (not 1.0 as in the pathfinding table).
BNG_UNIT_VALUE: dict[int, float] = {
    8: 8.0,
    6: 6.0,
    4: 4.0,
    2: 2.0,
    0: 0.0,  # sealed surfaces / very low distinctiveness = 0 BNG units
}

# ── Post-construction condition factors by distinctiveness ─────────────────
# Reflects how well the ADJACENT corridor strip recovers after construction
# disturbance, following DEFRA Metric 4.0 condition state guidance.
# High-distinctiveness habitats suffer severe damage and recover very slowly;
# low-distinctiveness grassland/modified land returns to Good condition quickly.
POST_CONSTRUCTION_CONDITION: dict[int, float] = {
    8: 0.3,  # Very high (blanket bog, calcareous grassland): remains Poor — irreplaceable
    6: 0.5,  # High (neutral meadow, reedbed, high-value woodland): Poor/Moderate
    4: 0.7,  # Medium (broadleaved woodland, hedgerow, pond): Moderate
    2: 1.0,  # Low (improved / modified grassland): recovers to Good within ~3 years
    0: 0.0,  # Very low: no habitat value before or after
}


def get_distinctiveness(habitat_type: str) -> int:
    """Return the distinctiveness score for a habitat type."""
    return BNG_WEIGHTS.get(habitat_type, DEFAULT_DISTINCTIVENESS)


def get_habitat_cost(habitat_type: str) -> float:
    """Return the A* cost for traversing a given habitat type."""
    d = get_distinctiveness(habitat_type)
    return DISTINCTIVENESS_COST.get(d, 2.0)
