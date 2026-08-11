import asyncio
from pathlib import Path
import json
import unittest
from unittest.mock import patch

from sqlmodel import Session, SQLModel, create_engine, select

from mission_intelligence import (
    MAX_EVIDENCE_ROWS,
    _csrf_token,
    _evaluation_workspace,
    build_decision_fingerprint,
    compute_evidence_analysis,
    import_evidence,
    parse_evidence_bytes,
    record_decision,
    validate_evidence_records,
)
from models import Customer, MissionDecisionRecord, MissionEvaluation, MissionEvidenceEvent, MissionEvidenceImport


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

    def test_upload_type_and_row_limit_are_enforced(self):
        with self.assertRaisesRegex(ValueError, "csv or .json"):
            parse_evidence_bytes("exercise.txt", b"not evidence")
        records = make_records() * ((MAX_EVIDENCE_ROWS // 16) + 1)
        _, result = validate_evidence_records(records)
        self.assertFalse(result["valid"])
        self.assertIn("no more than", result["errors"][0])

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
        self.assertIn("Download signed PDF", module)
        self.assertIn("Operator-owned decision", module)
        self.assertIn("get_customer_from_session", module)
        self.assertIn("Mission Release Gate", template)

    def test_decision_fingerprint_is_deterministic(self):
        evaluation = MissionEvaluation(
            customer_id=1,
            public_id="release-gate-1",
            name="Release Gate",
            workflow_name="Triage",
            hypothesis="Candidate is faster without more risk.",
            release_version="1.2.0",
            decision_owner="Program lead",
        )
        evidence_import = MissionEvidenceImport(
            customer_id=1,
            evaluation_id=1,
            revision=1,
            filename="evidence.json",
            dataset_sha256="a" * 64,
            validation_json="{}",
            analysis_json=json.dumps({"analysis_version": "HA-EVAL-001", "recommendation": {"action": "expand"}}),
            imported_by="owner@example.com",
        )
        from datetime import datetime
        signed_at = datetime(2026, 8, 11, 12, 0, 0)
        args = (evaluation, evidence_import, 1, "expand", "Guardrails held.", "Program lead", "This release only.", signed_at)
        self.assertEqual(build_decision_fingerprint(*args), build_decision_fingerprint(*args))
        changed = build_decision_fingerprint(evaluation, evidence_import, 1, "modify", "Guardrails held.", "Program lead", "This release only.", signed_at)
        self.assertNotEqual(build_decision_fingerprint(*args), changed)

    def test_imports_and_decisions_are_append_only(self):
        engine = create_engine("sqlite://")
        SQLModel.metadata.create_all(engine)

        class EvidenceFile:
            def __init__(self, filename, payload, content_type="application/json"):
                self.filename = filename
                self.content_type = content_type
                self.payload = payload

            async def read(self, _limit):
                return self.payload

        with Session(engine) as session:
            customer = Customer(company="Test Program", contact_email="owner@example.com")
            session.add(customer)
            session.commit()
            session.refresh(customer)
            evaluation = MissionEvaluation(
                customer_id=customer.id,
                public_id="gate-append-only",
                name="Release 1.2",
                workflow_name="Mission triage",
                hypothesis="Candidate reduces time without guardrail regression.",
                release_version="1.2.0",
                decision_owner="Program lead",
                guardrail_threshold=100.0,
            )
            session.add(evaluation)
            session.commit()
            session.refresh(evaluation)

            first_payload = json.dumps(make_records()).encode()
            second_records = make_records()
            second_records[0]["run_id"] = "RUN-REVISED"
            second_payload = json.dumps(second_records).encode()
            evidence_csrf = _csrf_token(customer.id, "evidence:%s" % evaluation.public_id)
            decision_csrf = _csrf_token(customer.id, "decision:%s" % evaluation.public_id)
            with patch("mission_intelligence._customer", return_value=customer):
                asyncio.run(import_evidence(evaluation.public_id, object(), EvidenceFile("first.json", first_payload), evidence_csrf, session))
                first_active = evaluation.active_import_id
                asyncio.run(import_evidence(evaluation.public_id, object(), EvidenceFile("second.json", second_payload), evidence_csrf, session))

                imports = list(session.exec(select(MissionEvidenceImport).where(
                    MissionEvidenceImport.evaluation_id == evaluation.id
                ).order_by(MissionEvidenceImport.revision)).all())
                events = list(session.exec(select(MissionEvidenceEvent).where(
                    MissionEvidenceEvent.evaluation_id == evaluation.id
                )).all())
                self.assertEqual([item.revision for item in imports], [1, 2])
                self.assertEqual(len(events), 32)
                self.assertNotEqual(first_active, evaluation.active_import_id)

                record_decision(
                    evaluation.public_id, object(), "expand", "Evidence supports controlled expansion.",
                    "Program lead", "Applies to this release and cohort set.", decision_csrf, session,
                )
                record_decision(
                    evaluation.public_id, object(), "modify", "A narrower release is required.",
                    "Program lead", "Applies to this release and cohort set.", decision_csrf, session,
                )
                decisions = list(session.exec(select(MissionDecisionRecord).where(
                    MissionDecisionRecord.evaluation_id == evaluation.id
                ).order_by(MissionDecisionRecord.revision)).all())
                self.assertEqual([item.revision for item in decisions], [1, 2])
                self.assertEqual([item.action for item in decisions], ["expand", "modify"])
                self.assertEqual(decisions[0].evidence_revision, 2)
                self.assertEqual(len({item.record_sha256 for item in decisions}), 2)
                rendered = _evaluation_workspace(evaluation, list(reversed(imports)), list(reversed(decisions)), customer.id)
                self.assertIn("Evidence and decision history", rendered)
                self.assertIn("Download signed PDF", rendered)
                self.assertIn("Decision D2", rendered)
                self.assertIn('<div class="decision-actions"><label>', rendered)
                self.assertIn('name="csrf_token"', rendered)


if __name__ == "__main__":
    unittest.main()
