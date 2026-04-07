"""
Mapping of PDF AcroForm field IDs to their data sources / LLM instructions.
Field IDs are the exact names as returned by pypdf's get_fields().
"""

# All text fields: field_id → instruction for the LLM.
# For factual/pass-through fields the instruction tells the model exactly which
# value to use; for narrative fields it asks for generated prose.
ALL_TEXT_FIELDS: dict[str, str] = {
    # ── Developer details (use provided values verbatim) ──────────────────
    "planningapprefnum": (
        "Planning application reference number. Use planning_app_ref from developer data, "
        "or 'Pending' if not provided."
    ),
    "13 Local planning authority LPA": (
        "Name of the Local Planning Authority. Use lpa from developer data."
    ),
    "development": (
        "Site address / location of development. Use site_address from developer data."
    ),
    "describedevelop": (
        "Brief description of the development. Use development_description from developer data."
    ),
    "applicantname": "Full name of the applicant. Use applicant_name from developer data.",
    "companyname":   "Company name. Use company_name from developer data.",
    "company name":  "Company name (duplicate field). Use company_name from developer data.",
    "name":          "Applicant name (duplicate field). Use applicant_name from developer data.",
    "emailaddress":  "Email address. Use email from developer data.",
    "telephonenumber": "Telephone number. Use telephone from developer data.",
    "address":       "Site address (duplicate field). Use site_address from developer data.",

    # ── Dates ─────────────────────────────────────────────────────────────
    "surveydate": (
        "Date of habitat survey in DD/MM/YYYY format. "
        "Derive from generated_at in development_details."
    ),

    # ── BNG metric — pre-development ──────────────────────────────────────
    "habitatbiodiversityunits": (
        "Total pre-development area habitat biodiversity units. "
        "Use total_pre_units from the metric (4 decimal places)."
    ),
    "hedgerow":   "Pre-development hedgerow biodiversity units. Enter '0' — not assessed.",
    "watercourse": "Pre-development watercourse biodiversity units. Enter '0' — not assessed.",

    # ── BNG metric — post-development ─────────────────────────────────────
    "Number of area habitat biodiversity units_2": (
        "Total post-development area habitat biodiversity units. "
        "Use total_post_units from the metric (4 decimal places)."
    ),
    "Number of hedgerow biodiversity units_2":    "Post-development hedgerow units. Enter '0'.",
    "Number of watercourse biodiversity units_2": "Post-development watercourse units. Enter '0'.",

    # ── BNG metric — net change ───────────────────────────────────────────
    "Area habitat biodiversity units": (
        "Net change in area habitat biodiversity units (may be negative). "
        "Use net_change_units from the metric (4 decimal places)."
    ),
    "Area habitat biodiversity units  change": (
        "Net percentage change in area habitat biodiversity units. "
        "Use net_change_percent from the metric (2 decimal places)."
    ),
    "Hedgerow biodiversity units":        "Net change in hedgerow units. Enter '0'.",
    "Hedgerow biodiversity units  change": "Net % change in hedgerow units. Enter '0'.",
    "Watercourse biodiversity units":      "Net change in watercourse units. Enter '0'.",
    "Watercourse biodiversity units  change": "Net % change in watercourse units. Enter '0'.",

    # ── Narrative fields (LLM-generated prose) ────────────────────────────
    "bng": (
        "Section 4.3 — 250 words or fewer. Explain how this development has met BNG guidance: "
        "the habitat types affected, the biodiversity metric outcome (pre/post units and % change), "
        "and how any deficit will be addressed through off-site compensation. "
        "Professional tone, suitable for LPA submission."
    ),
    "irreplaceablehabitats": (
        "Section 4.4 — 250 words or fewer. Explain how impacts to irreplaceable habitats "
        "(especially ancient woodland) have been avoided or minimised. "
        "If no irreplaceable habitats are affected, state that clearly."
    ),
    "surveyconstraints": (
        "Section 6.2 — 100 words or fewer. Describe the survey constraints and assumptions "
        "used in the baseline habitat assessment (satellite data, PHI, field-survey requirement)."
    ),
}

# Checkbox fields with AcroForm states: (field_id, condition_key, on_state, off_state)
# condition_key is evaluated in form_mapper.py against computed boolean conditions.
CHECKBOX_FIELDS: list[tuple[str, str, str, str]] = [
    ("Onsite",  "gain_onsite",   "/On", "/Off"),
    ("Offsite", "gain_offsite",  "/On", "/Off"),
    ("Both",    "gain_both",     "/On", "/Off"),
]

# Yes/No button fields: (field_id, condition_key)
YES_NO_FIELDS: list[tuple[str, str]] = [
    ("the planning application",                                    "pre_dev_date_same"),
    ("412 Do you have a habitat management and monitoring plan",    "has_hmp"),
    ("413 Have you used the statutory biodiversity metric tool",    "used_metric_tool"),
    ("If yes tell us if youve submitted an approved compensation plan", "impacts_irreplaceable"),
    ("52 Have you submitted an approved compensation plan",         "submitted_compensation"),
    ("81 Do you need to use statutory biodiversity credits",        "needs_credits"),
    ("Records Centre or other bodies",                              "share_data"),
]
