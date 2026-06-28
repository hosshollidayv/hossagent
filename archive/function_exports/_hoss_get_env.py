def _hoss_get_env(*names):
    for name in names:
        value = (_hoss_os.getenv(name) or "").strip()
        if value:
            return value
    return ""