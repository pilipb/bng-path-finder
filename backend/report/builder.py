"""
Biodiversity Gain Plan document builder.

Constructs a structured BGP document from a route calculation result,
following the DEFRA Biodiversity Gain Plan template structure.
"""

from datetime import datetime, timezone
from typing import TypedDict

from bng.weights import POST_CONSTRUCTION_CONDITION
from report.summariser import build_summary


ROAD_WIDTH_M = 6.0       # assumed single-track access road width (m)
SURVEY_CORRIDOR_M = 15.0 # ecological survey corridor width (m); DEFRA guidance
CONDITION_FACTOR = 1.0   # pre-development condition assumed "Good" throughout
MIN_GAIN_PERCENT = 10.0  # statutory minimum biodiversity net gain (Environment Act 2021)


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
    summary: str
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

        # Pre-development: full survey corridor at Good condition
        area_ha = (length_m * SURVEY_CORRIDOR_M) / 10_000

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

    # Post-development: road footprint seals ROAD_WIDTH_M of the corridor.
    # The remaining strip (SURVEY_CORRIDOR_M - ROAD_WIDTH_M) is retained but
    # its condition degrades during construction in proportion to how sensitive
    # the habitat is — high-distinctiveness habitats recover very slowly.
    post_dev: list[HabitatRow] = []
    for item in habitat_map.values():
        d = item["distinctiveness"]
        road_fraction = ROAD_WIDTH_M / SURVEY_CORRIDOR_M
        remaining_area_ha = item["area_ha"] * (1 - road_fraction)

        # Post-construction condition reflects habitat sensitivity (Metric 4.0)
        post_condition = POST_CONSTRUCTION_CONDITION.get(d, 1.0)
        condition_label = _condition_label(post_condition)
        remaining_units = (
            remaining_area_ha
            * _distinctiveness_to_unit_value(d)
            * post_condition
            * (1.15 if item["is_lnrs"] else 1.0)
        )

        if remaining_area_ha > 0:
            post_dev.append(HabitatRow(
                habitat_type=item["habitat_type"],
                area_ha=round(remaining_area_ha, 4),
                distinctiveness=d,
                condition=condition_label,
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

    doc = BGPDocument(
        title="Biodiversity Gain Plan",
        reference=reference,
        summary="",  # populated below once the document is assembled
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
    doc["summary"] = build_summary(doc, route_result)
    return doc


def _distinctiveness_to_unit_value(d: int) -> float:
    """Biodiversity Metric 4.0 unit value per distinctiveness band.
    Sealed/very-low surfaces score 0 (not 0.5 — corrected from earlier placeholder)."""
    return {8: 8.0, 6: 6.0, 4: 4.0, 2: 2.0, 0: 0.0}.get(d, 2.0)


def _condition_label(factor: float) -> str:
    """Map a Metric 4.0 condition factor to a human-readable label."""
    if factor >= 1.0:
        return "Good"
    if factor >= 0.7:
        return "Moderate"
    if factor >= 0.4:
        return "Poor"
    return "Very Poor"


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
