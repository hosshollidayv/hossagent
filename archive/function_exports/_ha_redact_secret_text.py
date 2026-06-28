def _ha_redact_secret_text(text):
    text = str(text or "")
    sam_key = _ha_get_sam_api_key() if "_ha_get_sam_api_key" in globals() else ""

    if sam_key:
        text = text.replace(sam_key, "[REDACTED_SAM_API_KEY]")

    # Redact common query-string form even if the key changes.
    text = re.sub(r"api_key=([^&\s]+)", "api_key=[REDACTED]", text)
    return text