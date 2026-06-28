def _hoss_fetch_federal_register(market):
    try:
        import requests
        query = f"{market} artificial intelligence evaluation testing assurance"
        r = requests.get(
            "https://www.federalregister.gov/api/v1/documents.json",
            params={
                "conditions[term]": query,
                "per_page": 25,
                "order": "newest",
            },
            timeout=12,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("results", []) or []
    except Exception as e:
        return [{"_hoss_error": str(e)}]