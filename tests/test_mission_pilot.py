from pathlib import Path
import json
import unittest

from mission_intelligence import (
    compute_evidence_analysis,
    parse_evidence_bytes,
    validate_evidence_records,
)


ROOT = Path(__file__).resolve().parents[1]


def make_records():
    records = []
    run_number = 1
    for cohort in ("Certified", "Trainee"):
        for variant in ("control", "treatment"):
            for index in range(4):
                records.append({
                    "run_id": "RUN-%03d" % run_number,
                    "operator_id": "%s-%02d" % (cohort[:3], index),
                    "cohort": cohort,
                    "variant": variant,
                    "workflow_seconds": 50 - index if variant == "control" else 40 - index,
                    "outcome_success": True,
                    "guardrail_triggered": cohort == "Trainee" and variant == "treatment" and index > 0,
                })
                run_number += 1
    return records


class MissionPilotTest(unittest.TestCase):
    def test_json_event_envelope_is_supported(self):
        payload = json.dumps({"events": make_records()}).encode()
        parsed = parse_evidence_bytes("exercise.json", payload)
        self.assertEqual(len(parsed), 16)

    def test_evidence_contract_normalizes_valid_rows(self):
        normalized, result = validate_evidence_records(make_records())
        self.assertTrue(result["valid"])
        self.assertEqual(result["rows_valid"], 16)
        self.assertEqual({row["variant"] for row in normalized}, {"control", "treatment"})

    def test_duplicate_run_blocks_import(self):
        records = make_records()
        records[1]["run_id"] = records[0]["run_id"]
        _, result = validate_evidence_records(records)
        self.assertFalse(result["valid"])
        self.assertTrue(any("duplicate run_id" in item for item in result["errors"]))

    def test_analysis_surfaces_cohort_guardrail_risk(self):
        normalized, result = validate_evidence_records(make_records())
        self.assertTrue(result["valid"])
        analysis = compute_evidence_analysis(normalized, guardrail_threshold=50.0)
        self.assertEqual(analysis["recommendation"]["action"], "modify")
        self.assertEqual(analysis["risk_cohorts"], ["Trainee"])

    def test_pilot_surface_includes_real_workflow(self):
        template = (ROOT / "templates" / "mission_pilot.html").read_text()
        module = (ROOT / "mission_intelligence.py").read_text()
        self.assertIn("Validate &amp; analyze", module)
        self.assertIn("Download PDF brief", module)
        self.assertIn("Operator-owned decision", module)
        self.assertIn("get_customer_from_session", module)
        self.assertIn("Pilot Workspace", template)


if __name__ == "__main__":
    unittest.main()
