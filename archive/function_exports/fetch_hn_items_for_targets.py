def fetch_hn_items_for_targets(targets, market):
    records = []
    seen = set()

    for target in targets:
        query = f'"{target}" "AI evaluation"'

        try:
            r = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": 10,
                },
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception:
            continue

        for hit in payload.get("hits", []) or []:
            object_id = hit.get("objectID") or hit.get("url") or hit.get("title")
            if not object_id or object_id in seen:
                continue

            seen.add(object_id)
            hit["_target"] = target
            records.append(hit)

    return records