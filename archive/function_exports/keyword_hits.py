def keyword_hits(text):
    low = (text or "").lower()
    hard = [k for k in HARD_AI_TERMS if k in low]
    soft = [k for k in SOFT_ADJACENCY_TERMS if k in low]
    return hard, soft