"""
Builds the complete field_id → value mapping for the BNG PDF form.

All text fields are populated via a single Claude API call that receives the
full project context and instructions for every field.  Checkbox / Yes-No
fields use simple boolean logic (AcroForm state values cannot be generated
as free text).
"""
import json
import logging
import os
from datetime import datetime

import anthropic

from bng.form_models import BNGFormInput
from bng.field_map import ALL_TEXT_FIELDS, CHECKBOX_FIELDS, YES_NO_FIELDS

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"


def build_field_values(inp: BNGFormInput) -> dict:
    """
    Return a complete field_id → value dict for all PDF form fields.

    Text fields:        single LLM call using full project context
    Checkbox / Yes-No:  computed from boolean conditions derived from the data
    """
    metric = inp.bgp_document.get("sections", {}).get("biodiversity_gain_metric", {})
    segments = inp.route_result.get("segments", [])

    # ── 1. LLM fills every text field ────────────────────────────────────────
    context = _build_context(inp, metric, segments)
    values = _llm_fill_text_fields(context)

    # ── 2. Checkbox fields (Onsite / Offsite / Both) ─────────────────────────
    gain_type = "both" if metric.get("gain_deficit", 0) > 0 else "on_site"
    checkbox_conditions = {
        "gain_onsite":  gain_type == "on_site",
        "gain_offsite": gain_type == "off_site",
        "gain_both":    gain_type == "both",
    }
    for field_id, condition_key, on_state, off_state in CHECKBOX_FIELDS:
        values[field_id] = on_state if checkbox_conditions.get(condition_key) else off_state

    # ── 3. Yes/No button fields ───────────────────────────────────────────────
    has_awi = any(s.get("ancient_woodland") for s in segments)
    yn_conditions = {
        "pre_dev_date_same":      True,
        "has_hmp":                True,
        "used_metric_tool":       True,
        "impacts_irreplaceable":  has_awi,
        "submitted_compensation": False,
        "needs_credits":          metric.get("gain_deficit", 0) > 0,
        "share_data":             True,
    }
    for field_id, condition_key in YES_NO_FIELDS:
        values[field_id] = "/Yes" if yn_conditions.get(condition_key) else "/Off"

    return values


# ── Context builder ──────────────────────────────────────────────────────────

def _build_context(inp: BNGFormInput, metric: dict, segments: list) -> dict:
    """Assemble all project data into one context dict for the LLM prompt."""
    dev = inp.developer
    sections = inp.bgp_document.get("sections", {})
    dev_details = sections.get("development_details", {})

    generated_at = dev_details.get("generated_at", "")
    try:
        survey_date = datetime.fromisoformat(generated_at).strftime("%d/%m/%Y")
    except Exception:
        survey_date = datetime.now().strftime("%d/%m/%Y")

    return {
        "developer": {
            "applicant_name":           dev.applicant_name or "",
            "company_name":             dev.company_name or "",
            "site_address":             dev.site_address or "",
            "lpa":                      dev.lpa or "",
            "planning_app_ref":         dev.planning_app_ref or "Pending",
            "development_description":  dev.development_description or "Access road construction",
            "email":                    dev.email or "",
            "telephone":                dev.telephone or "",
        },
        "development_details": {
            "generated_at": generated_at,
            "survey_date":  survey_date,
            "type":         dev_details.get("type", "Access road"),
            "road_width_m": dev_details.get("road_width_m", 6.0),
            "bbox_wgs84":   dev_details.get("coordinates", {}).get("bbox_wgs84", []),
        },
        "metric": {
            "total_pre_units":    metric.get("total_pre_units", 0),
            "total_post_units":   metric.get("total_post_units", 0),
            "net_change_units":   metric.get("net_change_units", 0),
            "net_change_percent": metric.get("net_change_percent", 0),
            "gain_deficit":       metric.get("gain_deficit", 0),
            "off_site_required":  metric.get("gain_deficit", 0) > 0,
        },
        "route": {
            "total_length_m":    inp.route_result.get("total_length_m", 0),
            "segment_count":     len(segments),
        },
        "constraints": {
            "sssi_consultation_required": sections.get("sssi_consultation_required", False),
            "ancient_woodland_impacted":  any(s.get("ancient_woodland") for s in segments),
            "lnrs_areas_crossed":         sections.get("lnrs_areas_crossed", []),
        },
        "pre_development_habitats": [
            {
                "habitat_type":         h["habitat_type"],
                "area_ha":              h["area_ha"],
                "distinctiveness":      h["distinctiveness"],
                "condition":            h["condition"],
                "strategic_significance": h["strategic_significance"],
                "units":                h["units"],
            }
            for h in sections.get("pre_development_habitat", [])
        ],
        "notes": sections.get("notes", ""),
        "bgp_reference": inp.bgp_document.get("reference", ""),
        "bgp_summary":   inp.bgp_document.get("summary", ""),
    }


# ── LLM call ─────────────────────────────────────────────────────────────────

def _llm_fill_text_fields(context: dict) -> dict:
    """
    Single Claude call: given the full project context, fill every text field.
    Falls back to static values if the API key is missing or the call fails.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — using fallback field values")
        return _fallback_text_fields(context)

    prompt = f"""You are completing an official UK Biodiversity Net Gain (BNG) planning form \
for an access road development.  Write concise, professional responses suitable for \
submission to a Local Planning Authority.

PROJECT DATA (use this as the authoritative source for all factual fields):
{json.dumps(context, indent=2)}

FIELDS TO COMPLETE — respond with a single JSON object mapping each field_id to its value. \
For factual/pass-through fields use the exact values from PROJECT DATA. \
For narrative fields write professional prose as instructed. \
No markdown, no preamble — JSON only.

{json.dumps(ALL_TEXT_FIELDS, indent=2)}"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if the model adds them
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        result = json.loads(raw)
        logger.info("LLM filled %d text fields", len(result))
        return result
    except Exception as e:
        logger.warning("LLM field fill failed: %s — using fallback", e)
        return _fallback_text_fields(context)


# ── Fallback ─────────────────────────────────────────────────────────────────

def _fallback_text_fields(context: dict) -> dict:
    """Static fallback used when Claude is unavailable."""
    dev = context["developer"]
    metric = context["metric"]
    constraints = context["constraints"]

    deficit = metric["gain_deficit"]
    bng_text = (
        f"This development has been assessed using the Statutory Biodiversity Metric 4.0. "
        f"Pre-development baseline: {metric['total_pre_units']:.4f} biodiversity units. "
        f"Post-development delivery: {metric['total_post_units']:.4f} units. "
        f"Net change: {metric['net_change_percent']:.2f}%. "
        + ("Off-site compensation will be secured to address the remaining deficit."
           if deficit > 0 else
           "The development delivers the required minimum 10% net gain.")
    )
    irr_text = (
        "Ancient woodland and other irreplaceable habitats within the route corridor have been "
        "identified. The proposed route has been optimised using biodiversity cost analysis to "
        "minimise impacts. Residual impacts will be subject to further consultation with Natural England."
        if constraints["ancient_woodland_impacted"] else
        "No irreplaceable habitats have been identified within the development footprint. "
        "All habitats present are within the scope of the Statutory Biodiversity Metric."
    )

    return {
        "planningapprefnum":                      dev["planning_app_ref"],
        "13 Local planning authority LPA":         dev["lpa"],
        "development":                             dev["site_address"],
        "describedevelop":                         dev["development_description"],
        "applicantname":                           dev["applicant_name"],
        "companyname":                             dev["company_name"],
        "company name":                            dev["company_name"],
        "name":                                    dev["applicant_name"],
        "emailaddress":                            dev["email"],
        "telephonenumber":                         dev["telephone"],
        "address":                                 dev["site_address"],
        "surveydate":                              context["development_details"]["survey_date"],
        "habitatbiodiversityunits":                f"{metric['total_pre_units']:.4f}",
        "hedgerow":                                "0",
        "watercourse":                             "0",
        "Number of area habitat biodiversity units_2": f"{metric['total_post_units']:.4f}",
        "Number of hedgerow biodiversity units_2": "0",
        "Number of watercourse biodiversity units_2": "0",
        "Area habitat biodiversity units":         f"{metric['net_change_units']:.4f}",
        "Area habitat biodiversity units  change": f"{metric['net_change_percent']:.2f}",
        "Hedgerow biodiversity units":             "0",
        "Hedgerow biodiversity units  change":     "0",
        "Watercourse biodiversity units":          "0",
        "Watercourse biodiversity units  change":  "0",
        "bng":                        bng_text,
        "irreplaceablehabitats":      irr_text,
        "surveyconstraints": (
            "Habitat assessment was conducted using satellite-derived data and the Natural England "
            "Priority Habitats Inventory. Field survey will be required prior to formal submission."
        ),
    }
