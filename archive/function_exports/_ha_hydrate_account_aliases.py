def _ha_hydrate_account_aliases(opportunities):
    hydrated = []

    for item in opportunities or []:
        if not isinstance(item, dict):
            continue

        x = dict(item)

        name = (
            x.get("agency")
            or x.get("account")
            or x.get("accountName")
            or x.get("company")
            or x.get("name")
            or "Unknown Account"
        )

        x["agency"] = name
        x["account"] = name
        x["accountName"] = name

        if not x.get("status_label"):
            score = x.get("score", 0) or 0
            if score >= 82:
                x["status_label"] = "High confidence"
                x["status"] = x.get("status") or "green"
            elif score >= 65:
                x["status_label"] = "Medium confidence"
                x["status"] = x.get("status") or "amber"
            else:
                x["status_label"] = "Watch"
                x["status"] = x.get("status") or "red"

        if not x.get("recommended_action"):
            x["recommended_action"] = f"Treat {name} as a recommended account for follow-up validation."

        hydrated.append(x)

    return hydrated