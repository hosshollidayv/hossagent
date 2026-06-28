def _hoss_has_env(*names):
    for name in names:
        value = (_hoss_os.getenv(name) or "").strip()
        if value:
            return True
    return False