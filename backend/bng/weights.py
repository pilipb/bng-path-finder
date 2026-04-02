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

# Cost multiplier per distinctiveness band
DISTINCTIVENESS_COST: dict[int, float] = {
    8: 8.0,
    6: 6.0,
    4: 4.0,
    2: 2.0,
    0: 1.0,
}


def get_distinctiveness(habitat_type: str) -> int:
    """Return the distinctiveness score for a habitat type."""
    return BNG_WEIGHTS.get(habitat_type, DEFAULT_DISTINCTIVENESS)


def get_habitat_cost(habitat_type: str) -> float:
    """Return the A* cost for traversing a given habitat type."""
    d = get_distinctiveness(habitat_type)
    return DISTINCTIVENESS_COST.get(d, 2.0)
