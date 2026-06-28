def _ha_get_sam_api_key():
    env_key = (
        os.getenv("SAM_API_KEY")
        or os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    ).strip()

    if env_key:
        return env_key

    secrets = _ha_read_local_secret_file()

    return (
        secrets.get("SAM_API_KEY")
        or secrets.get("SAM_GOV_API_KEY")
        or secrets.get("SAMGOV_API_KEY")
        or ""
    ).strip()