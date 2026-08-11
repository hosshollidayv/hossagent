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
        self.assertIn(
            "Requests are reviewed by an operator before access is granted.", worker
        )

    def test_successful_request_access_post_gets_a_customer_confirmation(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        css = (ROOT / "static" / "request-access.css").read_text()
        self.assertIn('request.method === "POST"', worker)
        self.assertIn("requestAccessSuccessHtml", worker)
        self.assertIn("We have what we need.", worker)
        self.assertIn("Your request is in.", worker)
        self.assertIn('href="/demos"', worker)
        self.assertIn(".request-success-card", css)
        self.assertIn(".success-actions", css)

    def test_signup_routes_to_request_access(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        self.assertIn('url.pathname === "/signup"', worker)
        self.assertIn('new URL("/request-access", request.url)', worker)
        self.assertNotIn("roleAwareOriginPage", worker)

    def test_login_is_positioned_as_owner_only(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        self.assertIn('url.pathname === "/login"', worker)
        self.assertIn("loginPage", worker)
        self.assertIn("Use your owner credentials.", worker)
        self.assertIn("Request early access", worker)

    def test_logout_clears_sessions_and_returns_to_login(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        self.assertIn('url.pathname === "/logout"', worker)
        self.assertIn('url.pathname === "/admin/logout"', worker)
        self.assertIn('new URL("/login?logout=true", request.url)', worker)
        self.assertIn("You have been signed out.", worker)
        self.assertIn('searchParams.get("logout") === "true"', worker)
        self.assertIn("hossagent_session=;", worker)
        self.assertIn("hossagent_admin=;", worker)
        self.assertIn('"Cache-Control": "no-store"', worker)
        self.assertIn('"X-HossAgent-Edge": "session-logout"', worker)

    def test_operator_command_represents_the_full_portfolio(self):
        page = (ROOT / "templates" / "operator.html").read_text()
        css = (ROOT / "static" / "operator.css").read_text()
        self.assertIn("Four decision engines.<br>One command center.", page)
        self.assertIn("From first signal to decisive action.", page)
        self.assertNotIn("Nothing hidden. Nothing orphaned.", page)
        self.assertNotIn("Surface registry", page)
        self.assertNotIn("fully represented", page)
        self.assertNotIn("product surfaces represented", page)
        self.assertNotIn("Route registry", page)
        self.assertNotIn(">Mapped<", page)
        self.assertNotIn(">Product surface<", page)
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

    def test_operational_surfaces_are_server_gated_to_owner_session(self):
        worker = (ROOT / "edge" / "worker.js").read_text()
        page = (ROOT / "templates" / "operator.html").read_text()
        self.assertIn("ownerClaimFromValidatedSession", worker)
        self.assertIn("isOwnerOnlyPath", worker)
        self.assertIn("ownerAccessGate", worker)
        self.assertIn('claims.role === "owner"', worker)
        self.assertIn("claims.auth === true", worker)
        self.assertIn('"/mission-intelligence/pilot"', worker)
        self.assertIn('"/portal"', worker)
        self.assertIn('new URL("/demos", request.url)', worker)
        self.assertNotIn("operatorHtmlForViewer", worker)
        self.assertIn("Demo only", page)
        self.assertIn("Working alpha", page)

    def test_public_copy_matches_release_readiness(self):
        landing = (ROOT / "templates" / "marketing_landing.html").read_text()
        mission = (ROOT / "templates" / "mission_intelligence.html").read_text()
        demos = (ROOT / "templates" / "demos.html").read_text()
        self.assertEqual(landing.count("Product access coming soon"), 4)
        self.assertIn("Self-guided demos available now.", landing)
        self.assertNotIn('href="/signup"', landing)
        self.assertNotIn('href="/login"', landing)
        self.assertIn("Operational workspace coming soon.", mission)
        self.assertNotIn('href="/mission-intelligence/pilot"', mission)
        self.assertIn("Product workspaces are coming soon", demos)

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

    def test_customer_copy_uses_role_aware_language(self):
        customer_facing_files = {
            *list((ROOT / "templates").glob("*.html")),
            *list((ROOT / "static").glob("*.js")),
            ROOT / "mission_intelligence.py",
            ROOT / "pipeline_health.py",
            ROOT / "product_demos.py",
            ROOT / "edge" / "worker.js",
        }
        for path in sorted(customer_facing_files):
            self.assertNotRegex(path.read_text(), r"(?i)\bhuman\b", str(path))


if __name__ == "__main__":
    unittest.main()
