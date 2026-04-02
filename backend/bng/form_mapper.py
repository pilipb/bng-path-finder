"""
Builds the complete field_id → value mapping for the BNG PDF form.
Handles direct data mapping and Claude-generated narrative fields.
"""
import json
import logging
import os
from datetime import datetime

import anthropic

from bng.form_models import BNGFormInput
from bng.field_map import DIRECT_TEXT_FIELDS, CHECKBOX_FIELDS, YES_NO_FIELDS, CLAUDE_FIELDS

logger = logging.getLogger(__name__)


def build_field_values(inp: BNGFormInput) -> dict:
    """
    Returns complete field_id → value dict for all PDF form fields.
    """
    values: dict = {}

    metric = inp.bgp_document.get("sections", {}).get("biodiversity_gain_metric", {})
    segments = inp.route_result.get("segments", [])
    dev_details = inp.bgp_document.get("sections", {}).get("development_details", {})

    # --- 1. Direct text fields ---
    computed_values = _compute_values(inp, metric, dev_details)
    for field_id, source, path in DIRECT_TEXT_FIELDS:
        val = computed_values.get(f"{source}.{path}")
        if val is not None:
            values[field_id] = str(val)

    # --- 2. Checkbox fields (Onsite/Offsite/Both) ---
    gain_type = _derive_gain_type(metric)
    conditions = {
        "gain_onsite":  gain_type == "on_site",
        "gain_offsite": gain_type == "off_site",
        "gain_both":    gain_type == "both",
    }
    for field_id, condition_key, on_state, off_state in CHECKBOX_FIELDS:
        values[field_id] = on_state if conditions.get(condition_key, False) else off_state

    # --- 3. Yes/No button fields (best-effort) ---
    has_awi = any(s.get("ancient_woodland") for s in segments)
    yn_conditions = {
        "pre_dev_date_same":      True,   # assume same date for prototype
        "has_hmp":                True,   # assume habitat mgmt plan exists
        "used_metric_tool":       True,
        "impacts_irreplaceable":  has_awi,
        "submitted_compensation": False,
        "needs_credits":          metric.get("gain_deficit", 0) > 0,
        "share_data":             True,
    }
    for field_id, condition_key in YES_NO_FIELDS:
        values[field_id] = "/Yes" if yn_conditions.get(condition_key, False) else "/Off"

    # --- 4. Claude narrative fields ---
    narrative_values = _generate_narratives(inp, metric, segments, has_awi)
    values.update(narrative_values)

    return values


def _compute_values(inp: BNGFormInput, metric: dict, dev_details: dict) -> dict:
    """Resolve all dot-path values into a flat lookup."""
    dev = inp.developer
    # Dates
    generated_at = dev_details.get("generated_at", "")
    try:
        survey_date = datetime.fromisoformat(generated_at).strftime("%d/%m/%Y")
    except Exception:
        survey_date = datetime.now().strftime("%d/%m/%Y")

    return {
        "developer.planning_app_ref":       dev.planning_app_ref or "Pending",
        "developer.lpa":                    dev.lpa or "",
        "developer.site_address":           dev.site_address or "",
        "developer.development_description": dev.development_description or "Access road construction",
        "developer.applicant_name":         dev.applicant_name or "",
        "developer.company_name":           dev.company_name or "",
        "developer.email":                  dev.email or "",
        "developer.telephone":              dev.telephone or "",
        "computed.survey_date":             survey_date,
        "computed.zero":                    "0",
        "metric.total_pre_units":           f"{metric.get('total_pre_units', 0):.4f}",
        "metric.total_post_units":          f"{metric.get('total_post_units', 0):.4f}",
        "metric.net_change_units":          f"{metric.get('net_change_units', 0):.4f}",
        "metric.net_change_percent":        f"{metric.get('net_change_percent', 0):.2f}",
    }


def _derive_gain_type(metric: dict) -> str:
    """Determine if gain is on-site, off-site, or both."""
    # For an access road tool, default is on-site only
    # If there's a deficit, off-site compensation is required
    if metric.get("gain_deficit", 0) > 0:
        return "both"
    return "on_site"


def _generate_narratives(inp: BNGFormInput, metric: dict, segments: list, has_awi: bool) -> dict:
    """Single Claude API call to generate all narrative fields."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — using placeholder narratives")
        return _placeholder_narratives(metric, has_awi)

    # Build project summary for context
    habitat_summary = _summarise_habitats(inp.bgp_document)
    project_context = json.dumps({
        "development_type": "Access road",
        "site_address": inp.developer.site_address or "England",
        "lpa": inp.developer.lpa or "Unknown LPA",
        "total_pre_dev_units": metric.get("total_pre_units", 0),
        "total_post_dev_units": metric.get("total_post_units", 0),
        "net_change_units": metric.get("net_change_units", 0),
        "net_change_percent": metric.get("net_change_percent", 0),
        "gain_deficit": metric.get("gain_deficit", 0),
        "off_site_required": metric.get("gain_deficit", 0) > 0,
        "sssi_consultation_required": inp.bgp_document.get("sections", {}).get("sssi_consultation_required", False),
        "ancient_woodland_impacted": has_awi,
        "lnrs_areas_crossed": inp.bgp_document.get("sections", {}).get("lnrs_areas_crossed", []),
        "habitat_types_affected": habitat_summary,
        "total_route_length_m": inp.route_result.get("total_length_m", 0),
        "notes": inp.bgp_document.get("sections", {}).get("notes", ""),
    }, indent=2)

    fields_to_generate = {k: v for k, v in CLAUDE_FIELDS.items()}

    prompt = f"""You are completing an official UK Biodiversity Net Gain (BNG) planning form for an access road development.
Write concise, professional responses suitable for submission to a Local Planning Authority.

PROJECT DATA:
{project_context}

FIELDS TO COMPLETE (respond with JSON only, field_id → text, max 250 words each):
{json.dumps({k: v for k, v in fields_to_generate.items()}, indent=2)}

Respond ONLY with a JSON object. No markdown, no preamble."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        return json.loads(raw)
    except Exception as e:
        logger.warning("Claude narrative generation failed: %s — using placeholders", e)
        return _placeholder_narratives(metric, has_awi)


def _summarise_habitats(bgp_doc: dict) -> list[str]:
    pre_hab = bgp_doc.get("sections", {}).get("pre_development_habitat", [])
    return [f"{h['habitat_type']} ({h['area_ha']:.3f} ha, {h['units']:.2f} units)" for h in pre_hab]


def _placeholder_narratives(metric: dict, has_awi: bool) -> dict:
    deficit = metric.get("gain_deficit", 0)
    bng_text = (
        f"This development has been assessed using the Statutory Biodiversity Metric 4.0. "
        f"The pre-development baseline totals {metric.get('total_pre_units', 0):.2f} biodiversity units. "
        f"Post-development, {metric.get('total_post_units', 0):.2f} units are delivered. "
        f"The net change is {metric.get('net_change_percent', 0):.1f}%. "
        + ("Off-site compensation will be secured to address the remaining deficit." if deficit > 0 else
           "The development delivers the required minimum 10% net gain.")
    )
    irr_text = (
        "Ancient woodland and other irreplaceable habitats within the route corridor have been identified. "
        "The proposed route has been optimised using biodiversity cost analysis to minimise impacts. "
        "Any residual impacts will be subject to further consultation with Natural England."
        if has_awi else
        "No irreplaceable habitats have been identified within the development footprint. "
        "All habitats present are within the scope of the Statutory Biodiversity Metric."
    )
    return {
        "bng": bng_text,
        "irreplaceablehabitats": irr_text,
        "surveyconstraints": (
            "Habitat assessment was conducted using satellite-derived data and the Natural England "
            "Priority Habitats Inventory. Field survey will be required prior to formal submission."
        ),
    }
