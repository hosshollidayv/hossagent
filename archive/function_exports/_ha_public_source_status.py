def _ha_public_source_status():
    sam_key = bool(_ha_get_sam_api_key())

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
            "status": "live" if sam_key else "needs_key",
            "job": "Active federal opportunities. Requires SAM.gov API key before activation." if not sam_key else "Active federal opportunities and solicitations.",
        },
    ]