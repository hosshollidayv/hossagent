from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MissionDemoTest(unittest.TestCase):
    def test_public_demo_route_is_registered(self):
        main = (ROOT / "main.py").read_text()
        self.assertIn('@app.get("/mission-intelligence/demo"', main)

    def test_demo_covers_complete_decision_chain(self):
        page = (ROOT / "templates" / "mission_demo.html").read_text()
        for phrase in (
            "Define the question",
            "Bring the evidence",
            "Validate the run",
            "Expose cohort risk",
            "Sign the disposition",
            "Export the record",
        ):
            self.assertIn(phrase, page)
        self.assertIn("No account, upload, or operational claim", page)

    def test_demo_has_autoplay_and_manual_controls(self):
        script = (ROOT / "static" / "mission-demo.js").read_text()
        self.assertEqual(script.count("label: \"0"), 6)
        self.assertIn("scheduleAdvance", script)
        self.assertIn("demo-play", script)
        self.assertIn("demo-restart", script)
        self.assertIn("data-step", (ROOT / "templates" / "mission_demo.html").read_text())

    def test_product_pages_link_to_demo(self):
        product = (ROOT / "templates" / "mission_intelligence.html").read_text()
        landing = (ROOT / "templates" / "marketing_landing.html").read_text()
        self.assertGreaterEqual(product.count('href="/mission-intelligence/demo"'), 3)
        self.assertIn('href="/mission-intelligence/demo"', landing)


if __name__ == "__main__":
    unittest.main()
