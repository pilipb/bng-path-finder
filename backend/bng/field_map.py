"""
Mapping of PDF AcroForm field IDs to their data sources.
Field IDs are the exact names as returned by pypdf's get_fields().
"""

# Direct text field mappings: field_id → (source, dot.path)
# source: "developer" | "metric" | "route" | "computed"
DIRECT_TEXT_FIELDS: list[tuple[str, str, str]] = [
    # Developer details
    ("planningapprefnum",               "developer", "planning_app_ref"),
    ("13 Local planning authority LPA", "developer", "lpa"),
    ("development",                     "developer", "site_address"),
    ("describedevelop",                 "developer", "development_description"),
    ("applicantname",                   "developer", "applicant_name"),
    ("companyname",                     "developer", "company_name"),
    ("company name",                    "developer", "company_name"),
    ("name",                            "developer", "applicant_name"),
    ("emailaddress",                    "developer", "email"),
    ("telephonenumber",                 "developer", "telephone"),
    ("address",                         "developer", "site_address"),
    # Dates
    ("surveydate",                      "computed",  "survey_date"),
    # BNG metric — pre-development
    ("habitatbiodiversityunits",        "metric",    "total_pre_units"),
    ("hedgerow",                        "computed",  "zero"),
    ("watercourse",                     "computed",  "zero"),
    # BNG metric — post-development
    ("Number of area habitat biodiversity units_2", "metric", "total_post_units"),
    ("Number of hedgerow biodiversity units_2",     "computed", "zero"),
    ("Number of watercourse biodiversity units_2",  "computed", "zero"),
    # BNG metric — net change
    ("Area habitat biodiversity units",             "metric",  "net_change_units"),
    ("Area habitat biodiversity units  change",     "metric",  "net_change_percent"),
    ("Hedgerow biodiversity units",                 "computed", "zero"),
    ("Hedgerow biodiversity units  change",         "computed", "zero"),
    ("Watercourse biodiversity units",              "computed", "zero"),
    ("Watercourse biodiversity units  change",      "computed", "zero"),
]

# Checkbox fields with known states: field_id → (condition_key, on_state, off_state)
# condition_key is evaluated in form_mapper.py
CHECKBOX_FIELDS: list[tuple[str, str, str, str]] = [
    ("Onsite",  "gain_onsite",   "/On", "/Off"),
    ("Offsite", "gain_offsite",  "/On", "/Off"),
    ("Both",    "gain_both",     "/On", "/Off"),
]

# Yes/No button fields (best-effort): field_id → condition_key
# These use /Yes and /Off — may not render in all viewers
YES_NO_FIELDS: list[tuple[str, str]] = [
    ("the planning application",                    "pre_dev_date_same"),
    ("412 Do you have a habitat management and monitoring plan", "has_hmp"),
    ("413 Have you used the statutory biodiversity metric tool", "used_metric_tool"),
    ("If yes tell us if youve submitted an approved compensation plan", "impacts_irreplaceable"),
    ("52 Have you submitted an approved compensation plan",     "submitted_compensation"),
    ("81 Do you need to use statutory biodiversity credits",   "needs_credits"),
    ("Records Centre or other bodies",             "share_data"),
]

# Fields Claude must generate: field_id → prompt description
CLAUDE_FIELDS: dict[str, str] = {
    "bng": (
        "Section 4.3: In 250 words or less, explain how this development has met BNG guidance. "
        "Focus on: the habitat types affected, the biodiversity metric outcome, and how any deficit "
        "will be addressed."
    ),
    "irreplaceablehabitats": (
        "Section 4.4: In 250 words or less, explain how impacts to irreplaceable habitats "
        "(especially ancient woodland) have been avoided or minimised. If no irreplaceable habitats "
        "are affected, state that clearly."
    ),
    "surveyconstraints": (
        "Section 6.2: In 100 words or less, describe the survey constraints and assumptions used "
        "in the baseline habitat assessment."
    ),
}
