async def _hoss_call_base_market_scan(payload):
    if _hoss_base_market_scan_endpoint is None:
        return {
            "status": "fallback",
            "message": "Base USAspending scan route was not found.",
            "opportunities": [],
            "source_status": [],
        }

    try:
        result = _hoss_base_market_scan_endpoint(payload)
        if _hoss_inspect.isawaitable(result):
            result = await result
        if isinstance(result, dict):
            return result
        if hasattr(result, "body"):
            import json
            return json.loads(result.body.decode("utf-8"))
        return {"status": "fallback", "message": "Base scan returned non-dict response.", "opportunities": []}
    except Exception as e:
        return {"status": "fallback", "message": f"Base USAspending scan failed: {e}", "opportunities": []}