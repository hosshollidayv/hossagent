def _ha_safe_te_matches(text):
    if "classify_te_stack_text" in globals():
        return classify_te_stack_text(text)

    low = (text or "").lower()
    fallback = {
        "evaluation": ["model evaluation", "test and evaluation", "evaluation", "testing", "assessment", "benchmark"],
        "monitoring": ["monitoring", "oversight", "runtime", "incident", "continuous", "telemetry"],
        "red_team": ["red team", "adversarial", "safety", "risk", "robustness", "stress testing"],
        "evidence_reporting": ["audit", "evidence", "reporting", "governance", "compliance", "assurance"],
        "agent_harness": ["agent", "agentic", "workflow", "orchestration", "artificial intelligence", "machine learning", "tool"],
    }

    matches = {}
    for category, terms in fallback.items():
        hits = [term for term in terms if term in low]
        if hits:
            matches[category] = sorted(set(hits))
    return matches