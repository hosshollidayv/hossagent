"""Build the public, no-login HossAgent surfaces for the Cloudflare edge."""

import html
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_demos import PRODUCT_DEMOS, serialize_product_demo
from pipeline_health import PIPELINE_HEALTH


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
write_template("operator.html", "operator/index.html")

for slug, pipeline in PIPELINE_HEALTH.items():
    stage_parts = []
    for number, name, volume, detail, status, label in pipeline["stages"]:
        repair = pipeline["repairs"].get(name)
        repair_control = ""
        if repair:
            action, result = repair
            repair_control = (
                '<button class="stage-repair" type="button" data-repair-stage data-stage="%s" '
                'data-repair-action="%s" data-repair-result="%s">%s <span aria-hidden="true">→</span></button>'
                % tuple(html.escape(value, quote=True) for value in (name, action, result, action))
            )
        stage_parts.append(
            '<article class="pipeline-stage" data-stage-card data-stage="%s" data-state="%s">'
            '<header><span>%s</span><em class="pipeline-status %s" data-stage-status>%s</em></header>'
            '<h3>%s</h3><p data-stage-detail>%s</p>'
            '<dl><div><dt>Input</dt><dd>%s</dd></div><div><dt>Posture</dt><dd data-stage-posture>%s</dd></div></dl>%s</article>'
            % (
                html.escape(name, quote=True),
                html.escape(status, quote=True),
                html.escape(number),
                html.escape(status),
                html.escape(label),
                html.escape(name),
                html.escape(detail),
                html.escape(volume),
                html.escape(label),
                repair_control,
            )
        )
    stages = "".join(stage_parts)
    checks = "".join(
        '<article class="pipeline-check" data-check data-state="%s"><header><span>%s</span><em class="%s" data-check-status>%s</em></header><strong data-check-percent>%s</strong><p data-check-count>%s covered</p></article>'
        % (
            html.escape(status, quote=True),
            html.escape(name),
            html.escape(status),
            html.escape("Needs review" if status != "healthy" else "Healthy"),
            html.escape(percent),
            html.escape(count),
        )
        for name, count, percent, status in pipeline["checks"]
    )
    blockers = "".join(
        '<div class="pipeline-blocker" role="row" data-blocker data-stage="%s"><span role="cell">%s</span><span role="cell">%s</span><span role="cell" data-blocker-reason>%s</span><span role="cell"><button type="button" data-blocker-repair data-stage="%s" data-repair-result="%s">%s <span aria-hidden="true">→</span></button></span></div>'
        % (
            html.escape(blocker[1], quote=True),
            html.escape(blocker[0]),
            html.escape(blocker[1]),
            html.escape(blocker[2]),
            html.escape(blocker[1], quote=True),
            html.escape(pipeline["repairs"][blocker[1]][1], quote=True),
            html.escape(blocker[3]),
        )
        for blocker in pipeline["blockers"]
    )
    replacements = {
        "%%PRODUCT_NAME%%": html.escape(pipeline["product_name"], quote=True),
        "%%DIVISION%%": html.escape(pipeline["division"], quote=True),
        "%%GLYPH%%": html.escape(pipeline["glyph"], quote=True),
        "%%THEME%%": html.escape(pipeline["theme"], quote=True),
        "%%HEADLINE%%": html.escape(pipeline["headline"]),
        "%%LEDE%%": html.escape(pipeline["lede"]),
        "%%DECISION%%": html.escape(pipeline["decision"]),
        "%%HEALTH_LABEL%%": html.escape(pipeline["health_label"]),
        "%%HEALTH_VALUE%%": html.escape(pipeline["health_value"]),
        "%%HEALTH_NUMBER%%": html.escape(pipeline["health_value"].rstrip("%"), quote=True),
        "%%HEALTH_NOTE%%": html.escape(pipeline["health_note"]),
        "%%GUARDRAIL%%": html.escape(pipeline["guardrail"]),
        "%%ARTIFACT%%": html.escape(pipeline["artifact"]),
        "%%DEMO_URL%%": html.escape(pipeline["demo_url"], quote=True),
        "%%STAGES%%": stages,
        "%%CHECKS%%": checks,
        "%%BLOCKERS%%": blockers,
    }
    write_template("pipeline_health.html", f"{slug}/pipeline/index.html", replacements)

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
    "request-access.css",
    "operator.css",
    "pipeline-health.css",
    "pipeline-health.js",
):
    shutil.copy2(ROOT / "static" / filename, static_output / filename)

print(f"Built {sum(1 for path in DIST.rglob('*') if path.is_file())} edge assets")
