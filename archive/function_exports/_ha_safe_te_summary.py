def _ha_safe_te_summary(matches):
    if "summarize_te_categories" in globals():
        return summarize_te_categories(matches)

    labels = {
        "evaluation": "Evaluation",
        "monitoring": "Monitoring",
        "red_team": "Red Teaming",
        "evidence_reporting": "Evidence / Reporting",
        "agent_harness": "Agent Harness",
    }

    ordered = ["evaluation", "monitoring", "red_team", "evidence_reporting", "agent_harness"]
    visible = [labels[k] for k in ordered if k in matches]
    return ", ".join(visible) if visible else "General AI demand"