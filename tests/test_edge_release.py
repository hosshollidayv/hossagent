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


if __name__ == "__main__":
    unittest.main()
