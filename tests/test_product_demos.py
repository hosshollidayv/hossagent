from pathlib import Path
import json
import unittest

from product_demos import PRODUCT_DEMOS, serialize_product_demo


ROOT = Path(__file__).resolve().parents[1]


class ProductDemosTest(unittest.TestCase):
    def test_every_non_mission_product_has_a_six_stage_demo(self):
        self.assertEqual(
            set(PRODUCT_DEMOS),
            {"public-sector", "private-sector", "property-intelligence"},
        )
        for slug, demo in PRODUCT_DEMOS.items():
            with self.subTest(slug=slug):
                self.assertEqual(len(demo["steps"]), 6)
                self.assertTrue(all(step.get("guardrail") for step in demo["steps"]))
                self.assertTrue(demo["steps"][-1].get("artifact"))

    def test_each_demo_enforces_its_distinct_action_boundary(self):
        public = json.dumps(PRODUCT_DEMOS["public-sector"])
        private = json.dumps(PRODUCT_DEMOS["private-sector"])
        property_demo = json.dumps(PRODUCT_DEMOS["property-intelligence"])
        self.assertIn("fake-pursuit", public.lower())
        self.assertIn("submission remains blocked", public.lower())
        self.assertIn("no buyer resolved", private.lower())
        self.assertIn("no autonomous send", private.lower())
        self.assertIn("owner unknown", property_demo.lower())
        self.assertIn("no autonomous outreach", property_demo.lower())

    def test_demo_routes_and_portfolio_hub_are_publicly_registered(self):
        main = (ROOT / "main.py").read_text()
        for route in (
            "/demos",
            "/public-sector/demo",
            "/private-sector/demo",
            "/property-intelligence/demo",
        ):
            self.assertIn(f'@app.get("{route}"', main)

    def test_landing_page_links_to_every_demo(self):
        landing = (ROOT / "templates" / "marketing_landing.html").read_text()
        for route in (
            "/demos",
            "/public-sector/demo",
            "/mission-intelligence/demo",
            "/private-sector/demo",
            "/property-intelligence/demo",
        ):
            self.assertIn(f'href="{route}"', landing)

    def test_shared_engine_has_autoplay_and_manual_controls(self):
        template = (ROOT / "templates" / "product_demo.html").read_text()
        script = (ROOT / "static" / "product-demo.js").read_text()
        self.assertIn('id="demo-play"', template)
        self.assertIn('id="demo-next"', template)
        self.assertIn('id="demo-restart"', template)
        self.assertIn("scheduleAdvance", script)
        self.assertIn("moveCursor", script)
        self.assertIn("ArrowRight", script)

    def test_embedded_config_serializer_escapes_closing_script_sequences(self):
        serialized = serialize_product_demo("public-sector")
        self.assertNotIn("</", serialized)
        self.assertEqual(json.loads(serialized), PRODUCT_DEMOS["public-sector"])


if __name__ == "__main__":
    unittest.main()
