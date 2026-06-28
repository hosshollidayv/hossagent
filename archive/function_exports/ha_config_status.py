async def ha_config_status():
    return {
        "ok": True,
        "config": {
            "sam_gov_api_key": _ha_env_present("SAM_GOV_API_KEY", "SAM_API_KEY", "SAMGOV_API_KEY"),
            "openai_api_key": _ha_env_present("OPENAI_API_KEY"),
        },
        "sources": {
            "usaspending": "configured",
            "federal_register": "configured",
            "sam_gov": "configured" if _ha_env_present("SAM_GOV_API_KEY", "SAM_API_KEY", "SAMGOV_API_KEY") else "missing",
            "openai": "configured" if _ha_env_present("OPENAI_API_KEY") else "missing",
        }
    }