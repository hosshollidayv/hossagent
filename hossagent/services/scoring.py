def score_from_evidence(evidence_count: int, source_count: int, has_active_motion: bool = False) -> int:
    score = 50
    score += min(evidence_count * 5, 25)
    score += min(source_count * 7, 21)
    if has_active_motion:
        score += 10
    return max(0, min(100, score))
