async def ha_market_scan(payload: dict | None = None):
    data = _ha_scan_payload()
    payload = payload or {}
    data["workspace"] = payload.get("workspace") or data["workspace"]
    data["business_unit"] = payload.get("business_unit") or data["business_unit"]
    data["market"] = payload.get("market") or data["market"]
    return data