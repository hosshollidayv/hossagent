def _ha_public_source_status_v6(sam_configured=False, sam_error=None, sam_records=0):
    if not sam_configured:
        sam_status = "needs_key"
        sam_job = "Active federal opportunities. Requires SAM.gov API key before activation."
    elif sam_error:
        sam_status = "needs_attention"
        sam_job = "SAM.gov key is configured, but the current query returned an API error. See eval diagnostics."
    else:
        sam_status = "live"
        sam_job = f"Active federal opportunities and solicitations. Last query returned {sam_records} matching record(s)."

    return [
        {
            "name": "USAspending",
            "status": "live",
            "job": "Recent federal award history, agencies, vendors, and spend patterns.",
        },
        {
            "name": "Federal Register",
            "status": "live",
            "job": "Recent AI policy, governance, risk, and test-and-evaluation movement.",
        },
        {
            "name": "SAM.gov",
            "status": sam_status,
            "job": sam_job,
        },
    ]