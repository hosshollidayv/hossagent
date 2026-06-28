def fetch_gdelt_articles_for_targets(targets, market):
    records = []
    seen = set()

    for target in targets:
        query = f'"{target}" ("AI evaluation" OR "model evaluation" OR "red teaming" OR "AI governance" OR "AI safety" OR "agentic")'

        try:
            r = requests.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params={
                    "query": query,
                    "mode": "ArtList",
                    "format": "json",
                    "maxrecords": 10,
                    "sort": "HybridRel",
                },
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception:
            continue

        for article in payload.get("articles", []) or []:
            url = article.get("url")
            title = article.get("title")
            key = url or title

            if not key or key in seen:
                continue

            seen.add(key)
            article["_target"] = target
            records.append(article)

    return records