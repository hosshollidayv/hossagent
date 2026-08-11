from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class EdgeReleaseTest(unittest.TestCase):
    def test_worker_only_overrides_public_product_surfaces(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        for route in (
            '"/"',
            '"/demos"',
            '"/mission-intelligence"',
            '"/mission-intelligence/demo"',
            '"/public-sector/demo"',
            '"/private-sector/demo"',
            '"/property-intelligence/demo"',
        ):
            self.assertIn(route, worker)
        self.assertIn("return fetch(request)", worker)
        self.assertIn('url.pathname === "/request-access"', worker)
        self.assertIn('url.pathname === "/operator"', worker)
        self.assertIn('origin.status !== 200', worker)
        self.assertIn('"operator-command"', worker)
        self.assertIn("enhanceRequestAccess", worker)

    def test_worker_targets_hossagent_without_origin_changes(self):
        config = (ROOT / "wrangler.jsonc").read_text()
        self.assertIn('"pattern": "hossagent.net/*"', config)
        self.assertIn('"run_worker_first": true', config)

    def test_product_config_is_csp_safe(self):
        page = (ROOT / "templates" / "product_demo.html").read_text()
        script = (ROOT / "static" / "product-demo.js").read_text()
        self.assertIn('type="application/json"', page)
        self.assertNotIn("window.HOSS_PRODUCT_DEMO =", page)
        self.assertIn("JSON.parse(configNode.textContent)", script)

    def test_request_access_keeps_the_origin_form_and_adds_responsive_styles(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        css = (ROOT / "static" / "request-access.css").read_text()
        self.assertIn("const origin = await fetch(originRequest)", worker)
        self.assertIn("request-access.css", worker)
        self.assertIn("@media (max-width: 620px)", css)
        self.assertIn("font-size: 16px", css)
        self.assertIn(".form-card input:focus", css)

    def test_operator_command_represents_the_full_portfolio(self):
        page = (ROOT / "templates" / "operator.html").read_text()
        css = (ROOT / "static" / "operator.css").read_text()
        for product in (
            "Public Sector",
            "Mission Intelligence",
            "Private Sector",
            "Property Intelligence",
        ):
            self.assertIn(product, page)
        for route in (
            'href="/public-sector/demo"',
            'href="/mission-intelligence/demo"',
            'href="/mission-intelligence/pilot"',
            'href="/private-sector/demo"',
            'href="/property-intelligence/demo"',
            'href="/demos"',
            'href="/request-access"',
            'href="/portal"',
        ):
            self.assertIn(route, page)
        self.assertIn("@media (max-width: 720px)", css)
        self.assertIn("grid-template-columns: 1fr", css)

    def test_missing_product_pipeline_health_surfaces_are_protected_and_rendered(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        operator = (ROOT / "templates" / "operator.html").read_text()
        template = (ROOT / "templates" / "pipeline_health.html").read_text()
        css = (ROOT / "static" / "pipeline-health.css").read_text()
        script = (ROOT / "static" / "pipeline-health.js").read_text()
        config = (ROOT / "pipeline_health.py").read_text()
        for slug in ("public-sector", "private-sector", "property-intelligence"):
            self.assertIn(f'"/{slug}/pipeline"', worker)
            self.assertIn(f'href="/{slug}/pipeline"', operator)
            self.assertIn(f'"{slug}"', config)
        self.assertIn('new URL("/operator", request.url)', worker)
        self.assertIn('redirect: "manual"', worker)
        self.assertIn('"pipeline-health"', worker)
        self.assertIn("Illustrative pipeline health", template)
        self.assertIn("Product connectors must be live", template)
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn("Repair all broken stages", template)
        self.assertIn("Approve repaired set", template)
        self.assertIn("runAllRepairs", script)
        self.assertIn("repairStage", script)
        self.assertIn("sessionStorage", script)
        self.assertIn("window.setTimeout(runAllRepairs, 900)", script)
        self.assertIn("pipeline-health.js", worker)


if __name__ == "__main__":
    unittest.main()
