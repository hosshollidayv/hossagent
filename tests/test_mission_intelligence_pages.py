from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MissionIntelligencePagesTest(unittest.TestCase):
    def test_main_registers_mission_intelligence_route(self):
        main = (ROOT / "main.py").read_text()
        self.assertIn('@app.get("/mission-intelligence"', main)
        self.assertIn('app.mount("/static"', main)

    def test_landing_page_has_two_ingress_paths(self):
        landing = (ROOT / "templates" / "marketing_landing.html").read_text()
        self.assertGreaterEqual(landing.count('href="/mission-intelligence"'), 2)
        self.assertIn("Public Sector / Mission Release Gate", landing)

    def test_product_page_discloses_synthetic_data(self):
        page = (ROOT / "templates" / "mission_intelligence.html").read_text()
        self.assertIn("Synthetic exercise data", page)
        self.assertIn("All figures are fictional and synthetic", page)
        self.assertIn("data-cohort=\"trainee\"", page)
        self.assertIn("Generate evidence brief", page)

    def test_shared_brand_styles_cover_mission_surface(self):
        css = (ROOT / "static" / "web.css").read_text()
        self.assertIn("--accent: #c8f16b", css)
        self.assertIn(".mission-hero", css)
        self.assertIn(".evidence-grid", css)


if __name__ == "__main__":
    unittest.main()
