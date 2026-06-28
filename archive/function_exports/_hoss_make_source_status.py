def _hoss_make_source_status(sam_count=None, fed_count=None):
    sam_key = _hoss_get_env("SAM_GOV_API_KEY", "SAM_API_KEY", "SAMGOV_API_KEY")
    return [
        {
            "name": "USAspending",
            "status": "live",
            "job": "Recent federal award history, agencies, vendors, and spend patterns.",
        },
        {
            "name": "Federal Register",
            "status": "live" if fed_count is None or fed_count > 0 else "configured",
            "job": f"Recent AI policy, governance, risk, and test-and-evaluation movement. Last query returned {fed_count if fed_count is not None else 'available'} document(s).",
        },
        {
            "name": "SAM.gov",
            "status": "live" if sam_key and (sam_count or 0) > 0 else ("configured" if sam_key else "missing"),
            "job": (
                f"Active federal opportunities and solicitations. Last query returned {sam_count} matching record(s)."
                if sam_key and sam_count is not None
                else "Active federal opportunities and solicitations. Requires SAM.gov API key."
            ),
        },
    ]