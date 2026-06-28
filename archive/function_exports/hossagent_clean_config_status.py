async def hossagent_clean_config_status():
    sam_key = _hoss_get_env("SAM_GOV_API_KEY", "SAM_API_KEY", "SAMGOV_API_KEY")
    openai_key = _hoss_get_env("OPENAI_API_KEY")
    return {
        "ok": True,
        "config": {
            "sam_gov_api_key": bool(sam_key),
            "openai_api_key": bool(openai_key),
        },
        "sources": {
            "usaspending": "configured",
            "federal_register": "configured",
            "sam_gov": "configured" if sam_key else "missing",
            "openai": "configured" if openai_key else "missing",
        },
        "masked": {
            "sam_gov_api_key": _hoss_mask(sam_key),
            "openai_api_key": _hoss_mask(openai_key),
        },
    }