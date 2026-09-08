from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HossTrackerReleaseTest(unittest.TestCase):
    def test_overview_is_a_bounded_customer_facing_product_surface(self):
        page = (ROOT / "templates" / "hosstracker.html").read_text()
        self.assertIn("The six questions HossTracker is designed to answer", page)
        self.assertIn("Synthetic demo data", page)
        self.assertIn("No blocker recorded", page)
        self.assertIn("Email moves messages. HossTracker moves work.", page)
        self.assertIn("HOSS-7F31-A892-D118", page)
        self.assertIn("Shared work. Separate authority.", page)
        self.assertIn('href="/hosstracker/demo"', page)
        self.assertNotIn("72% complete", page)

    def test_overview_has_responsive_accessible_status_treatment(self):
        page = (ROOT / "templates" / "hosstracker.html").read_text()
        css = (ROOT / "static" / "hosstracker.css").read_text()
        self.assertIn('aria-label="The six questions HossTracker is designed to answer"', page)
        self.assertIn("Healthy", page)
        self.assertIn("At risk", page)
        self.assertIn("Overdue", page)
        self.assertIn("Blocked", page)
        self.assertIn("Unowned", page)
        self.assertIn("@media (max-width: 580px)", css)
        self.assertIn(".tracker-status-pill", css)

    def test_edge_build_publishes_tracker_overview_demo_and_styles(self):
        renderer = (ROOT / "edge" / "render_edge_assets.py").read_text()
        worker = (ROOT / "edge" / "worker.js").read_text()
        self.assertIn('write_template("hosstracker.html", "hosstracker/index.html")', renderer)
        self.assertIn('"hosstracker.css"', renderer)
        self.assertIn('"/static/hosstracker.css"', worker)
        self.assertIn('["/hosstracker", "/hosstracker/index.html"]', worker)
        self.assertIn('["/hosstracker/demo", "/hosstracker/demo/index.html"]', worker)


if __name__ == "__main__":
    unittest.main()
