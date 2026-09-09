import json
import unittest
from pathlib import Path

from hosstracker_scenarios import (
    HOSSTRACKER_SCENARIOS,
    serialize_hosstracker_scenario,
)

ROOT = Path(__file__).resolve().parents[1]


class HossTrackerScenariosTest(unittest.TestCase):
    def test_catalog_contains_three_ordered_concrete_stories(self):
        self.assertEqual(
            list(HOSSTRACKER_SCENARIOS),
            ["public-records", "dental-readiness", "prior-authorization"],
        )

    def test_each_story_matches_the_shared_six_stage_demo_contract(self):
        required_demo_fields = {
            "productName",
            "division",
            "theme",
            "headline",
            "intro",
            "workspace",
            "workspaceMeta",
            "overviewUrl",
            "catalogUrl",
            "catalogLabel",
            "boundary",
            "finishLabel",
            "finishTitle",
            "finishCta",
            "steps",
        }
        required_step_fields = {
            "navTitle",
            "navMeta",
            "label",
            "caption",
            "state",
            "kicker",
            "title",
            "description",
            "sourceTitle",
            "sources",
            "metrics",
            "records",
            "recommendationLabel",
            "recommendation",
            "recommendationDetail",
            "guardrailLabel",
            "guardrail",
            "guardrailDetail",
            "guardrailTone",
            "actionLabel",
            "toast",
        }

        for slug, demo in HOSSTRACKER_SCENARIOS.items():
            with self.subTest(slug=slug):
                self.assertTrue(required_demo_fields.issubset(demo))
                self.assertEqual(demo["overviewUrl"], "/hosstracker")
                self.assertEqual(demo["catalogUrl"], "/hosstracker/demo")
                self.assertEqual(demo["catalogLabel"], "Use cases")
                self.assertEqual(len(demo["steps"]), 6)
                for step in demo["steps"]:
                    self.assertTrue(required_step_fields.issubset(step))
                    self.assertEqual(len(step["sources"]), 3)
                    self.assertEqual(len(step["metrics"]), 3)
                    self.assertEqual(len(step["records"]), 3)
                    self.assertIn(step["guardrailTone"], {"pass", "hold", "block"})
                self.assertIn("artifact", demo["steps"][-1])

    def test_story_details_are_concrete_and_keep_consequential_decisions_bounded(self):
        public_records = json.dumps(HOSSTRACKER_SCENARIOS["public-records"]).lower()
        dental = json.dumps(HOSSTRACKER_SCENARIOS["dental-readiness"]).lower()
        healthcare = json.dumps(HOSSTRACKER_SCENARIOS["prior-authorization"]).lower()

        self.assertIn("jordan lee", public_records)
        self.assertIn("prr-2026-001887", public_records)
        self.assertIn("no autonomous mutation", public_records)

        self.assertIn("dd form 2813", dental)
        self.assertIn("hoss-8d42-b117-2813", dental)
        self.assertIn("readiness clerk", dental)
        self.assertIn("no phi", dental)

        self.assertIn("action_required", healthcare)
        self.assertIn("authorized clinical reviewer", healthcare)
        self.assertIn("no medical judgment", healthcare)
        self.assertIn("no phi", healthcare)

        for story in (public_records, dental, healthcare):
            self.assertIn("fictional", story)
            self.assertIn("no live", story)

    def test_hub_links_every_story_and_does_not_revive_property_intelligence(self):
        hub = (ROOT / "templates" / "hosstracker_demo_hub.html").read_text()
        for slug in HOSSTRACKER_SCENARIOS:
            self.assertIn(f'href="/hosstracker/demo/{slug}"', hub)
        self.assertIn("Pick the problem that feels familiar.", hub)
        self.assertIn("Everything in these walkthroughs is fictional and synthetic.", hub)
        self.assertNotIn("Property Intelligence", hub)

    def test_origin_and_edge_register_the_catalog_and_story_routes(self):
        main = (ROOT / "main.py").read_text()
        worker = (ROOT / "edge" / "worker.js").read_text()
        self.assertIn('@app.get("/hosstracker/demo"', main)
        self.assertIn('@app.get("/hosstracker/demo/{scenario_slug}"', main)
        self.assertIn('templates/hosstracker_demo_hub.html', main)
        for slug in HOSSTRACKER_SCENARIOS:
            self.assertIn(f'["/hosstracker/demo/{slug}",', worker)

    def test_embedded_story_json_escapes_closing_script_sequences(self):
        for slug, story in HOSSTRACKER_SCENARIOS.items():
            with self.subTest(slug=slug):
                serialized = serialize_hosstracker_scenario(slug)
                self.assertNotIn("</", serialized)
                self.assertEqual(json.loads(serialized), story)


if __name__ == "__main__":
    unittest.main()
