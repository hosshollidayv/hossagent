def _ha_status_from_score(score):
    try:
        score = int(score or 0)
    except Exception:
        score = 0

    if score >= 82:
        return "green", "High confidence"
    if score >= 65:
        return "amber", "Medium confidence"
    return "red", "Watch"