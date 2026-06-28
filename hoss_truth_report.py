from pathlib import Path
import re

ROOT = Path(".")
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".env", ".yaml", ".yml"}

hardcoded_terms = [
    "DEPT OF DEFENSE", "HEALTH AND HUMAN SERVICES", "VETERANS AFFAIRS",
    "COMMERCE DEPARTMENT", "SECURITIES AND EXCHANGE", "score", "mock", "fixture",
    "fallback", "demo"
]

connector_terms = [
    "requests.", "httpx", "api.sam.gov", "sam.gov", "usaspending",
    "federalregister", "openai", "OPENAI_API_KEY", "SAM_API_KEY"
]

route_terms = ["@app.route", "FastAPI", "/api/", "/eval", "self-test", "scan"]

def scan(terms):
    hits = []
    for path in ROOT.rglob("*"):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXT:
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if any(t.lower() in line.lower() for t in terms):
                    hits.append((str(path), i, line.strip()[:220]))
    return hits

hard = scan(hardcoded_terms)
conn = scan(connector_terms)
routes = scan(route_terms)

print("\n== HOSS TRUTH REPORT ==")
print(f"Hardcoded/demo/fallback indicators: {len(hard)}")
print(f"Connector/API indicators: {len(conn)}")
print(f"Route/scan/eval indicators: {len(routes)}")

print("\n-- Connector/API hits --")
for h in conn[:80]:
    print(f"{h[0]}:{h[1]}: {h[2]}")

print("\n-- Hardcoded/fallback hits --")
for h in hard[:120]:
    print(f"{h[0]}:{h[1]}: {h[2]}")

truth = 50
if conn:
    truth += 15
if routes:
    truth += 10
if len(hard) > 25:
    truth -= 15
elif len(hard) > 10:
    truth -= 8

truth = max(5, min(90, truth))
print(f"\nEstimated truthiness: {truth}%")
print("Read: above 70% = real pipeline with some fallback; 45-70% = demo shell with real plumbing; below 45% = mostly staged.")
