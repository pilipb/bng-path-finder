"""
Biodiversity Gain Plan document builder.

Constructs a structured BGP document from a route calculation result,
following the DEFRA Biodiversity Gain Plan template structure.
"""

from datetime import datetime, timezone
from typing import TypedDict


ROAD_WIDTH_M = 6.0          # assumed access road width
CONDITION_FACTOR = 1.0      # "Good" condition assumed throughout
MIN_GAIN_PERCENT = 10.0     # statutory minimum BNG requirement


class HabitatRow(TypedDict):
    habitat_type: str
    area_ha: float
    distinctiveness: int
    condition: str
    strategic_significance: str
    units: float


class BiodiversityGainMetric(TypedDict):
    total_pre_units: float
    total_post_units: float
    net_change_units: float
    net_change_percent: float
    minimum_gain_required: float
    gain_deficit: float


class BGPSections(TypedDict):
    development_details: dict
    pre_development_habitat: list[HabitatRow]
    post_development_habitat: list[HabitatRow]
    biodiversity_gain_metric: BiodiversityGainMetric
    off_site_compensation_required: bool
    sssi_consultation_required: bool
    lnrs_areas_crossed: list[str]
    notes: str


class BGPDocument(TypedDict):
    title: str
    reference: str
    sections: BGPSections


def build_gain_plan(route_result: dict) -> BGPDocument:
    """
    Build a Biodiversity Gain Plan document from a route calculation result.

    The plan models:
    - Pre-development: the habitat currently in the path corridor
    - Post-development: same corridor with road footprint removed (6m wide)
    - The net BNG impact and whether off-site compensation is required
    """
    segments: list[dict] = route_result.get("segments", [])
    total_length_m: float = route_result.get("total_length_m", 0.0)
    bbox: list[float] = route_result.get("bbox_wgs84", [0, 0, 0, 0])

    timestamp = datetime.now(timezone.utc)
    reference = f"BGP-{timestamp.strftime('%Y%m%d-%H%M%S')}"

    # Aggregate segments by habitat type
    habitat_map: dict[str, dict] = {}
    for seg in segments:
        hab = seg.get("habitat_type", "Unknown")
        d = seg.get("distinctiveness", 2)
        length_m = seg.get("length_m", 0.0)
        is_lnrs = seg.get("lnrs_flag", False)
        is_awi = seg.get("ancient_woodland", False)

        # Pre-development: full corridor width (assume 15m survey corridor)
        corridor_width_m = 15.0
        area_ha = (length_m * corridor_width_m) / 10_000

        strategic_sig = _strategic_significance(is_lnrs, is_awi)
        lnrs_multiplier = 1.15 if is_lnrs else 1.0
        units = area_ha * _distinctiveness_to_unit_value(d) * CONDITION_FACTOR * lnrs_multiplier

        if hab not in habitat_map:
            habitat_map[hab] = {
                "habitat_type": hab,
                "area_ha": 0.0,
                "distinctiveness": d,
                "condition": "Good",
                "strategic_significance": strategic_sig,
                "units": 0.0,
                "is_lnrs": is_lnrs,
                "is_awi": is_awi,
            }
        habitat_map[hab]["area_ha"] += area_ha
        habitat_map[hab]["units"] += units

    pre_dev: list[HabitatRow] = []
    for item in habitat_map.values():
        pre_dev.append(HabitatRow(
            habitat_type=item["habitat_type"],
            area_ha=round(item["area_ha"], 4),
            distinctiveness=item["distinctiveness"],
            condition=item["condition"],
            strategic_significance=item["strategic_significance"],
            units=round(item["units"], 4),
        ))

    # Post-development: road footprint (ROAD_WIDTH_M) destroys habitat
    # remaining corridor is ROAD_WIDTH_M narrower
    post_dev: list[HabitatRow] = []
    for item in habitat_map.values():
        # Fraction of corridor that becomes road
        road_fraction = ROAD_WIDTH_M / 15.0
        remaining_area_ha = item["area_ha"] * (1 - road_fraction)
        remaining_units = item["units"] * (1 - road_fraction)

        # Road surface itself is distinctiveness 0 (sealed surface)
        road_area_ha = item["area_ha"] * road_fraction

        if remaining_area_ha > 0:
            post_dev.append(HabitatRow(
                habitat_type=item["habitat_type"],
                area_ha=round(remaining_area_ha, 4),
                distinctiveness=item["distinctiveness"],
                condition=item["condition"],
                strategic_significance=item["strategic_significance"],
                units=round(remaining_units, 4),
            ))

    # Add sealed road surface as new habitat type in post-dev
    if total_length_m > 0:
        road_area_ha = (total_length_m * ROAD_WIDTH_M) / 10_000
        post_dev.append(HabitatRow(
            habitat_type="Sealed surface (new road)",
            area_ha=round(road_area_ha, 4),
            distinctiveness=0,
            condition="N/A",
            strategic_significance="None",
            units=0.0,
        ))

    # Totals
    total_pre_units = sum(r["units"] for r in pre_dev)
    total_post_units = sum(r["units"] for r in post_dev)
    net_change = total_post_units - total_pre_units
    net_change_pct = (net_change / total_pre_units * 100) if total_pre_units > 0 else 0.0

    # Minimum 10% gain required means post must be >= pre x 1.10
    minimum_required = total_pre_units * (MIN_GAIN_PERCENT / 100)
    gain_deficit = max(0.0, minimum_required - (total_post_units - total_pre_units))

    metric = BiodiversityGainMetric(
        total_pre_units=round(total_pre_units, 4),
        total_post_units=round(total_post_units, 4),
        net_change_units=round(net_change, 4),
        net_change_percent=round(net_change_pct, 2),
        minimum_gain_required=round(minimum_required, 4),
        gain_deficit=round(gain_deficit, 4),
    )

    sssi_required = any(s.get("sssi_flag") for s in segments)
    lnrs_areas = _get_lnrs_area_names(segments)

    # Ancient woodland note
    awi_segments = [s for s in segments if s.get("ancient_woodland")]
    notes_parts = []
    if awi_segments:
        n = len(awi_segments)
        notes_parts.append(
            f"WARNING: {n} path segment(s) pass through or adjacent to Ancient Woodland. "
            "Ancient Woodland is irreplaceable -- the BNG metric does not fully apply. "
            "An alternative route avoiding this area is strongly recommended."
        )
    if sssi_required:
        notes_parts.append(
            "This route triggers mandatory SSSI consultation with Natural England "
            "before any development can proceed."
        )
    if not notes_parts:
        notes_parts.append(
            "BNG units calculated using Statutory Biodiversity Metric 4.0. "
            "Habitat condition assumed 'Good' throughout. "
            "Actual on-site assessment required before submission."
        )

    return BGPDocument(
        title="Biodiversity Gain Plan",
        reference=reference,
        sections=BGPSections(
            development_details={
                "generated_at": timestamp.isoformat(),
                "type": "Access road",
                "road_width_m": ROAD_WIDTH_M,
                "coordinates": {
                    "bbox_wgs84": bbox,
                },
            },
            pre_development_habitat=pre_dev,
            post_development_habitat=post_dev,
            biodiversity_gain_metric=metric,
            off_site_compensation_required=gain_deficit > 0,
            sssi_consultation_required=sssi_required,
            lnrs_areas_crossed=lnrs_areas,
            notes=" ".join(notes_parts),
        ),
    )


def _distinctiveness_to_unit_value(d: int) -> float:
    """Biodiversity Metric 4.0 unit multiplier per distinctiveness band."""
    return {8: 8.0, 6: 6.0, 4: 4.0, 2: 2.0, 0: 0.5}.get(d, 2.0)


def _strategic_significance(is_lnrs: bool, is_awi: bool) -> str:
    if is_awi:
        return "Irreplaceable habitat"
    if is_lnrs:
        return "LNRS Strategic Significance"
    return "None"


def _get_lnrs_area_names(segments: list[dict]) -> list[str]:
    """Return list of unique LNRS area indicators from segments."""
    lnrs_segs = [s for s in segments if s.get("lnrs_flag")]
    if not lnrs_segs:
        return []
    return [f"LNRS area (segment {s['index'] + 1})" for s in lnrs_segs[:3]]
