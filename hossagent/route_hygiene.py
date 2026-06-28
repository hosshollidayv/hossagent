from collections import OrderedDict

def dedupe_routes_keep_latest(app):
    """
    FastAPI preserves route registration order.
    This keeps the newest route for each path+method pair and removes ghosts.
    """
    latest = OrderedDict()

    for route in app.router.routes:
        path = getattr(route, "path", None)
        methods = tuple(sorted(getattr(route, "methods", []) or []))
        endpoint = getattr(route, "endpoint", None)

        if not path or not methods:
            key = (path, id(route))
        else:
            key = (path, methods)

        latest[key] = route

    app.router.routes = list(latest.values())
    return app


def route_inventory(app):
    rows = []
    for route in app.router.routes:
        path = getattr(route, "path", "")
        methods = ",".join(sorted(getattr(route, "methods", []) or []))
        endpoint = getattr(getattr(route, "endpoint", None), "__name__", "")
        rows.append({"methods": methods, "path": path, "endpoint": endpoint})
    return sorted(rows, key=lambda r: (r["path"], r["methods"], r["endpoint"]))
