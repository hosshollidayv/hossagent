"""Build the public, no-login HossAgent surfaces for the Cloudflare edge."""

import html
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_demos import PRODUCT_DEMOS, serialize_product_demo


DIST = ROOT / "edge" / "dist"


def write_template(source: str, destination: str, replacements=None):
    content = (ROOT / "templates" / source).read_text()
    content = content.replace("{ga_script}", "")
    for token, value in (replacements or {}).items():
        content = content.replace(token, value)
    output = DIST / destination
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)


if DIST.exists():
    shutil.rmtree(DIST)

write_template("marketing_landing.html", "index.html")
write_template("demos.html", "demos/index.html")
write_template("mission_intelligence.html", "mission-intelligence/index.html")
write_template("mission_demo.html", "mission-intelligence/demo/index.html")

for slug, demo in PRODUCT_DEMOS.items():
    values = {
        "%%META_DESCRIPTION%%": html.escape(demo["intro"], quote=True),
        "%%PRODUCT_NAME%%": html.escape(demo["productName"], quote=True),
        "%%DEMO_THEME%%": html.escape(demo["theme"], quote=True),
        "%%DIVISION%%": html.escape(demo["division"], quote=True),
        "%%OVERVIEW_URL%%": html.escape(demo["overviewUrl"], quote=True),
        "%%HEADLINE%%": html.escape(demo["headline"], quote=True),
        "%%INTRO%%": html.escape(demo["intro"], quote=True),
        "%%BOUNDARY%%": html.escape(demo["boundary"], quote=True),
        "%%WORKSPACE%%": html.escape(demo["workspace"], quote=True),
        "%%WORKSPACE_META%%": html.escape(demo["workspaceMeta"], quote=True),
        "%%DEMO_CONFIG%%": serialize_product_demo(slug),
    }
    write_template("product_demo.html", f"{slug}/demo/index.html", values)

static_output = DIST / "static"
static_output.mkdir(parents=True, exist_ok=True)
for filename in (
    "web.css",
    "mission-demo.css",
    "mission-demo.js",
    "portfolio-demo.css",
    "product-demo.js",
):
    shutil.copy2(ROOT / "static" / filename, static_output / filename)

print(f"Built {sum(1 for path in DIST.rglob('*') if path.is_file())} edge assets")
