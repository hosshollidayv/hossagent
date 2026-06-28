def _hoss_mask(value):
    value = (value or "").strip()
    if not value:
        return None
    if len(value) <= 8:
        return "configured"
    return f"{value[:4]}...{value[-4:]}"