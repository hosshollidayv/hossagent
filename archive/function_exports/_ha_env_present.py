def _ha_env_present(*names):
    return any((_ha_os.getenv(name) or "").strip() for name in names)