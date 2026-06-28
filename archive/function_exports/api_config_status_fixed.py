def api_config_status_fixed():
    import os

    def configured(name: str) -> bool:
        return bool((os.getenv(name) or "").strip())

    sam_key = (
        os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAM_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    )

    return {
        "ok": True,
        "config": {
            "sam_gov_api_key": bool(sam_key.strip()),
            "openai_api_key": configured("OPENAI_API_KEY"),
        },
        "sources": {
            "sam_gov": "configured" if sam_key.strip() else "missing",
            "openai": "configured" if configured("OPENAI_API_KEY") else "missing",
        },
    }