def _ha_read_local_secret_file():
    path = Path(".hossagent.secrets")
    values = {}

    if not path.exists():
        return values

    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    except Exception:
        return {}

    return values