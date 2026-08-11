"""Protected workflow for the HossAgent Mission Release Gate."""

import csv
import hashlib
import hmac
import html
import io
import json
import re
import secrets
from datetime import datetime
from statistics import median
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session, select

from auth_utils import SESSION_COOKIE_NAME, get_customer_from_session, get_session_secret
from database import get_session
from models import (
    Customer,
    MissionDecisionRecord,
    MissionEvaluation,
    MissionEvidenceEvent,
    MissionEvidenceImport,
)


router = APIRouter(prefix="/mission-intelligence/pilot", tags=["mission-intelligence"])

REQUIRED_EVIDENCE_FIELDS = (
    "run_id",
    "operator_id",
    "cohort",
    "variant",
    "workflow_seconds",
    "outcome_success",
    "guardrail_triggered",
)
DECISION_ACTIONS = {"expand", "modify", "stop", "collect_more"}
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_ROWS = 25000
ALLOWED_EVIDENCE_SUFFIXES = {"csv", "json"}
ALLOWED_EVIDENCE_CONTENT_TYPES = {
    "",
    "application/json",
    "application/octet-stream",
    "text/csv",
    "text/json",
    "text/plain",
}
ACTION_LABELS = {
    "expand": "GO",
    "modify": "MODIFY",
    "stop": "HOLD",
    "collect_more": "HOLD · MORE EVIDENCE",
}


def _clean(value: Any, limit: int = 240) -> str:
    return str(value or "").strip()[:limit]


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "evaluation"


def _action_label(action: Optional[str]) -> str:
    return ACTION_LABELS.get(action or "", "NOT RECORDED")


def _canonical_sha256(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _csrf_token(customer_id: int, purpose: str) -> str:
    message = "%s:%s" % (customer_id, purpose)
    return hmac.new(get_session_secret().encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()


def _require_csrf(customer_id: int, purpose: str, token: str) -> None:
    if not hmac.compare_digest(_csrf_token(customer_id, purpose), token or ""):
        raise HTTPException(status_code=403, detail="Invalid form token")


def build_decision_fingerprint(
    evaluation: MissionEvaluation,
    evidence_import: MissionEvidenceImport,
    revision: int,
    action: str,
    rationale: str,
    approved_by: str,
    claim_boundary: str,
    signed_at: datetime,
) -> str:
    """Create a deterministic fingerprint for one signed release disposition."""
    analysis = json.loads(evidence_import.analysis_json or "{}")
    return _canonical_sha256({
        "record_schema": "HA-DECISION-001",
        "evaluation_public_id": evaluation.public_id,
        "evidence_revision": evidence_import.revision,
        "decision_revision": revision,
        "dataset_sha256": evidence_import.dataset_sha256,
        "analysis_version": analysis.get("analysis_version", evaluation.analysis_version),
        "system_recommendation": analysis.get("recommendation", {}).get("action", ""),
        "action": action,
        "rationale": rationale,
        "approved_by": approved_by,
        "claim_boundary": claim_boundary,
        "signed_at": signed_at.isoformat() + "Z",
    })


def _parse_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "pass", "success"}:
        return True
    if normalized in {"false", "0", "no", "n", "fail", "failure"}:
        return False
    return None


def parse_evidence_bytes(filename: str, payload: bytes) -> List[Dict[str, Any]]:
    """Parse a CSV or JSON evidence file into records."""
    text = payload.decode("utf-8-sig")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in ALLOWED_EVIDENCE_SUFFIXES:
        raise ValueError("Evidence files must use a .csv or .json extension.")
    if suffix == "json":
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed = parsed.get("events")
        if not isinstance(parsed, list):
            raise ValueError("JSON must be an array or an object with an events array.")
        if not all(isinstance(item, dict) for item in parsed):
            raise ValueError("Every JSON event must be an object.")
        return parsed
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV header row is missing.")
    return [dict(row) for row in reader]


def validate_evidence_records(records: Iterable[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Normalize evidence records and return structured validation results."""
    normalized: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    seen_runs = set()
    records = list(records)

    if not records:
        return [], {"valid": False, "rows_received": 0, "rows_valid": 0, "errors": ["The evidence file is empty."], "warnings": []}
    if len(records) > MAX_EVIDENCE_ROWS:
        return [], {
            "valid": False,
            "rows_received": len(records),
            "rows_valid": 0,
            "completeness_pct": 0,
            "errors": ["Evidence files may contain no more than %s rows." % MAX_EVIDENCE_ROWS],
            "warnings": [],
        }

    for row_number, raw in enumerate(records, start=2):
        row = {str(key).strip().lower(): value for key, value in raw.items() if key is not None}
        missing = [
            field for field in REQUIRED_EVIDENCE_FIELDS
            if row.get(field) is None or (isinstance(row.get(field), str) and not row.get(field).strip())
        ]
        if missing:
            errors.append("Row %s: missing %s." % (row_number, ", ".join(missing)))
            continue

        run_id = _clean(row.get("run_id"), 120)
        if run_id in seen_runs:
            errors.append("Row %s: duplicate run_id %s." % (row_number, run_id))
            continue
        seen_runs.add(run_id)

        operator_id = _clean(row.get("operator_id"), 120)
        if "@" in operator_id or " " in operator_id:
            warnings.append("Row %s: operator_id may contain identifying information; use a pseudonymous key." % row_number)

        variant_raw = _clean(row.get("variant"), 60).lower()
        variant_map = {
            "control": "control",
            "baseline": "control",
            "a": "control",
            "treatment": "treatment",
            "candidate": "treatment",
            "b": "treatment",
        }
        variant = variant_map.get(variant_raw)
        if not variant:
            errors.append("Row %s: variant must be control or treatment." % row_number)
            continue

        try:
            workflow_seconds = float(row.get("workflow_seconds"))
            if workflow_seconds <= 0 or workflow_seconds > 86400:
                raise ValueError
        except (TypeError, ValueError):
            errors.append("Row %s: workflow_seconds must be greater than 0 and no more than 86400." % row_number)
            continue

        outcome_success = _parse_bool(row.get("outcome_success"))
        guardrail_triggered = _parse_bool(row.get("guardrail_triggered"))
        if outcome_success is None or guardrail_triggered is None:
            errors.append("Row %s: outcome_success and guardrail_triggered must be true or false." % row_number)
            continue

        normalized.append({
            "source_row": row_number,
            "event_time": _clean(row.get("event_time"), 80) or None,
            "run_id": run_id,
            "operator_id": operator_id,
            "cohort": _clean(row.get("cohort"), 80),
            "variant": variant,
            "workflow_seconds": workflow_seconds,
            "outcome_success": outcome_success,
            "guardrail_triggered": guardrail_triggered,
        })

    variants = {row["variant"] for row in normalized}
    if "control" not in variants:
        errors.append("No control rows were found.")
    if "treatment" not in variants:
        errors.append("No treatment rows were found.")

    unique_operators = len({row["operator_id"] for row in normalized})
    if normalized and unique_operators < 4:
        warnings.append("Fewer than four pseudonymous operators are represented.")

    result = {
        "valid": not errors,
        "rows_received": len(records),
        "rows_valid": len(normalized),
        "completeness_pct": round((len(normalized) / len(records)) * 100, 1) if records else 0,
        "errors": errors[:30],
        "warnings": list(dict.fromkeys(warnings))[:20],
        "required_fields": list(REQUIRED_EVIDENCE_FIELDS),
    }
    return normalized, result


def _summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {"count": 0, "median_seconds": None, "outcome_rate": None, "guardrail_rate": None}
    return {
        "count": len(rows),
        "median_seconds": round(float(median([row["workflow_seconds"] for row in rows])), 1),
        "outcome_rate": round(sum(1 for row in rows if row["outcome_success"]) / len(rows) * 100, 1),
        "guardrail_rate": round(sum(1 for row in rows if row["guardrail_triggered"]) / len(rows) * 100, 1),
    }


def compute_evidence_analysis(records: List[Dict[str, Any]], guardrail_threshold: float, primary_direction: str = "lower") -> Dict[str, Any]:
    """Compute transparent control/treatment comparisons by cohort."""
    cohort_names = sorted({row["cohort"] for row in records}, key=str.lower)
    cohorts: List[Dict[str, Any]] = []
    for cohort_name in ["All operators"] + cohort_names:
        cohort_rows = records if cohort_name == "All operators" else [row for row in records if row["cohort"] == cohort_name]
        control = _summarize([row for row in cohort_rows if row["variant"] == "control"])
        treatment = _summarize([row for row in cohort_rows if row["variant"] == "treatment"])
        time_delta_pct = None
        outcome_delta = None
        guardrail_delta = None
        if control["median_seconds"] and treatment["median_seconds"] is not None:
            time_delta_pct = round((treatment["median_seconds"] - control["median_seconds"]) / control["median_seconds"] * 100, 1)
        if control["outcome_rate"] is not None and treatment["outcome_rate"] is not None:
            outcome_delta = round(treatment["outcome_rate"] - control["outcome_rate"], 1)
        if control["guardrail_rate"] is not None and treatment["guardrail_rate"] is not None:
            guardrail_delta = round(treatment["guardrail_rate"] - control["guardrail_rate"], 1)
        sufficient = control["count"] >= 3 and treatment["count"] >= 3
        breach = treatment["guardrail_rate"] is not None and treatment["guardrail_rate"] > guardrail_threshold
        cohorts.append({
            "name": cohort_name,
            "control": control,
            "treatment": treatment,
            "time_delta_pct": time_delta_pct,
            "outcome_delta_points": outcome_delta,
            "guardrail_delta_points": guardrail_delta,
            "sufficient": sufficient,
            "guardrail_breach": breach,
        })

    overall = cohorts[0]
    risk_cohorts = [row["name"] for row in cohorts[1:] if row["guardrail_breach"]]
    insufficient = [row["name"] for row in cohorts if not row["sufficient"]]
    time_improved = overall["time_delta_pct"] is not None and (
        overall["time_delta_pct"] < 0 if primary_direction == "lower" else overall["time_delta_pct"] > 0
    )
    outcome_not_worse = overall["outcome_delta_points"] is not None and overall["outcome_delta_points"] >= 0

    if insufficient:
        recommendation = {
            "action": "collect_more",
            "status": "Insufficient evidence",
            "title": "Collect more eligible runs.",
            "basis": "At least three control and three treatment runs are required in every reviewed cohort.",
        }
    elif risk_cohorts:
        recommendation = {
            "action": "modify",
            "status": "Cohort risk",
            "title": "Modify before broader exposure.",
            "basis": "%s crossed the %.1f%% guardrail threshold." % (", ".join(risk_cohorts), guardrail_threshold),
        }
    elif time_improved and outcome_not_worse and not overall["guardrail_breach"]:
        recommendation = {
            "action": "expand",
            "status": "Guardrails healthy",
            "title": "Expand through a controlled release.",
            "basis": "The primary workflow measure improved, the outcome did not regress, and the defined guardrail remained healthy.",
        }
    else:
        recommendation = {
            "action": "collect_more",
            "status": "Decision unresolved",
            "title": "Hold exposure and collect more evidence.",
            "basis": "The current result does not support expansion under the declared outcome and guardrail rules.",
        }

    return {
        "analysis_version": "HA-EVAL-001",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "row_count": len(records),
        "operator_count": len({row["operator_id"] for row in records}),
        "cohorts": cohorts,
        "risk_cohorts": risk_cohorts,
        "recommendation": recommendation,
        "claim_boundary": "Results support a decision only for the imported runs, declared cohorts, release assignment, outcome definition, and guardrail threshold. They do not establish performance outside this evaluation.",
    }


def _customer(request: Request, session: Session) -> Optional[Customer]:
    return get_customer_from_session(session, request.cookies.get(SESSION_COOKIE_NAME))


def _owned_evaluation(session: Session, customer_id: int, public_id: str) -> MissionEvaluation:
    evaluation = session.exec(select(MissionEvaluation).where(
        MissionEvaluation.customer_id == customer_id,
        MissionEvaluation.public_id == public_id,
    )).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


def _active_import(session: Session, evaluation: MissionEvaluation) -> Optional[MissionEvidenceImport]:
    if not evaluation.active_import_id:
        return None
    return session.exec(select(MissionEvidenceImport).where(
        MissionEvidenceImport.id == evaluation.active_import_id,
        MissionEvidenceImport.evaluation_id == evaluation.id,
        MissionEvidenceImport.customer_id == evaluation.customer_id,
        MissionEvidenceImport.valid == True,  # noqa: E712
    )).first()


def _current_decision(session: Session, evaluation: MissionEvaluation) -> Optional[MissionDecisionRecord]:
    if not evaluation.active_import_id:
        return None
    return session.exec(select(MissionDecisionRecord).where(
        MissionDecisionRecord.evaluation_id == evaluation.id,
        MissionDecisionRecord.customer_id == evaluation.customer_id,
        MissionDecisionRecord.import_id == evaluation.active_import_id,
    ).order_by(MissionDecisionRecord.revision.desc())).first()


def _redirect(public_id: str, notice: str) -> RedirectResponse:
    url = "/mission-intelligence/pilot?evaluation=%s&notice=%s" % (quote_plus(public_id), quote_plus(notice))
    return RedirectResponse(url=url, status_code=303)


def _format_number(value: Optional[float], suffix: str = "") -> str:
    if value is None:
        return "—"
    if float(value).is_integer():
        return "%d%s" % (int(value), suffix)
    return "%.1f%s" % (value, suffix)


def _analysis_html(evaluation: MissionEvaluation, analysis: Optional[Dict[str, Any]]) -> str:
    if not analysis:
        return '<div class="pilot-empty"><span>02</span><h3>No computed evidence yet.</h3><p>Import the event contract to calculate control and treatment results.</p></div>'
    overall = analysis["cohorts"][0]
    treatment = overall["treatment"]
    recommendation = analysis["recommendation"]
    rows = []
    for cohort in analysis["cohorts"]:
        state = "Breach" if cohort["guardrail_breach"] else ("Ready" if cohort["sufficient"] else "More runs")
        tone = "breach" if cohort["guardrail_breach"] else ("healthy" if cohort["sufficient"] else "watch")
        rows.append(
            '<div class="pilot-result-row"><strong>%s</strong><span>%s / %s</span><span>%s</span><span>%s</span><span>%s</span><em class="%s">%s</em></div>' % (
                html.escape(cohort["name"]),
                cohort["control"]["count"],
                cohort["treatment"]["count"],
                _format_number(cohort["treatment"]["median_seconds"], "s"),
                _format_number(cohort["treatment"]["outcome_rate"], "%"),
                _format_number(cohort["treatment"]["guardrail_rate"], "%"),
                tone,
                state,
            )
        )
    return """
      <div class="pilot-metrics">
        <article><span>Treatment median</span><strong>%s</strong><p>%s%% vs control</p></article>
        <article><span>Outcome success</span><strong>%s</strong><p>%s pts vs control</p></article>
        <article><span>Guardrail rate</span><strong>%s</strong><p>Threshold %.1f%%</p></article>
        <article><span>Eligible runs</span><strong>%s</strong><p>%s operators</p></article>
      </div>
      <div class="pilot-recommendation %s"><p>System recommendation · %s</p><h3>%s</h3><span>%s</span></div>
      <div class="pilot-results"><div class="pilot-result-head"><span>Cohort</span><span>Control / treatment</span><span>Median</span><span>Outcome</span><span>Guardrail</span><span>Status</span></div>%s</div>
    """ % (
        _format_number(treatment["median_seconds"], "s"),
        _format_number(overall["time_delta_pct"]),
        _format_number(treatment["outcome_rate"], "%"),
        _format_number(overall["outcome_delta_points"]),
        _format_number(treatment["guardrail_rate"], "%"),
        evaluation.guardrail_threshold,
        analysis["row_count"],
        analysis["operator_count"],
        html.escape(recommendation["action"]),
        html.escape(recommendation["status"]),
        html.escape(recommendation["title"]),
        html.escape(recommendation["basis"]),
        "".join(rows),
    )


def _validation_html(validation: Optional[Dict[str, Any]]) -> str:
    if not validation:
        return '<div class="validation-state neutral"><strong>Awaiting evidence</strong><span>The required schema is checked before any row enters the analysis.</span></div>'
    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])
    tone = "healthy" if validation.get("valid") else "breach"
    heading = "Evidence contract accepted" if validation.get("valid") else "Import blocked"
    detail = "%s of %s rows passed · %s%% complete" % (
        validation.get("rows_valid", 0), validation.get("rows_received", 0), validation.get("completeness_pct", 0)
    )
    items = "".join('<li>%s</li>' % html.escape(item) for item in errors + warnings)
    return '<div class="validation-state %s"><strong>%s</strong><span>%s</span>%s</div>' % (
        tone, heading, detail, '<ul>%s</ul>' % items if items else ""
    )


def _history_html(imports: List[MissionEvidenceImport], decisions: List[MissionDecisionRecord]) -> str:
    import_rows = "".join(
        '<div class="history-row"><span>E%s</span><strong>%s</strong><em class="%s">%s</em><small>%s rows · %s…</small></div>' % (
            item.revision,
            html.escape(item.filename),
            "healthy" if item.valid else "breach",
            "Accepted" if item.valid else "Blocked",
            item.row_count,
            html.escape(item.dataset_sha256[:12]),
        ) for item in imports
    ) or '<div class="history-empty">No evidence revisions recorded.</div>'
    decision_rows = "".join(
        '<div class="history-row"><span>D%s</span><strong>%s</strong><em>%s</em><small>%s · %s…</small></div>' % (
            item.revision,
            _action_label(item.action),
            html.escape(item.approved_by),
            item.signed_at.strftime("%Y-%m-%d %H:%M UTC"),
            html.escape(item.record_sha256[:12]),
        ) for item in decisions
    ) or '<div class="history-empty">No signed decisions recorded.</div>'
    return '<article class="pilot-stage history-stage"><div class="pilot-stage-head"><span>04</span><div><p>Release record</p><h2>Evidence and decision history.</h2></div></div><div class="history-grid"><section><h3>Evidence revisions</h3>%s</section><section><h3>Signed decisions</h3>%s</section></div></article>' % (import_rows, decision_rows)


def _evaluation_workspace(
    evaluation: MissionEvaluation,
    imports: List[MissionEvidenceImport],
    decisions: List[MissionDecisionRecord],
    customer_id: int,
) -> str:
    validation = json.loads(evaluation.validation_json) if evaluation.validation_json else None
    analysis = json.loads(evaluation.analysis_json) if evaluation.analysis_json else None
    current_decision = next((item for item in decisions if item.import_id == evaluation.active_import_id), None)
    active_import = next((item for item in imports if item.id == evaluation.active_import_id), None)
    decision_label = _action_label(evaluation.decision_action)
    checked = evaluation.decision_action or (analysis or {}).get("recommendation", {}).get("action", "modify")
    action_options = "".join(
        '<label><input type="radio" name="decision_action" value="%s" %s><span>%s</span></label>' % (
            action, "checked" if checked == action else "", label
        ) for action, label in (("expand", "GO"), ("modify", "MODIFY"), ("stop", "HOLD"), ("collect_more", "HOLD · MORE EVIDENCE"))
    )
    export_actions = (
        '<div class="export-actions"><a href="/mission-intelligence/pilot/%s/brief" target="_blank">Open release record</a><a href="/mission-intelligence/pilot/%s/brief.pdf">Download signed PDF</a></div>' % (evaluation.public_id, evaluation.public_id)
        if current_decision else '<div class="export-actions export-locked"><span>Sign a disposition to unlock the release record.</span></div>'
    )
    revision_line = "Evidence E%s" % active_import.revision if active_import else "No active evidence"
    if current_decision:
        revision_line += " · Decision D%s · %s…" % (current_decision.revision, current_decision.record_sha256[:12])
    return """
      <section class="pilot-workspace">
        <div class="pilot-workspace-head"><div><p class="eyebrow">Active release gate</p><h1>%s</h1><p>%s</p></div><div class="pilot-status"><span>%s</span><strong>%s</strong><small>%s</small></div></div>
        <div class="pilot-definition">
          <div><span>Workflow</span><strong>%s</strong></div><div><span>Release</span><strong>%s</strong></div><div><span>Primary measure</span><strong>%s · %s is better</strong></div><div><span>Guardrail</span><strong>%s ≤ %.1f%%</strong></div><div><span>Decision owner</span><strong>%s</strong></div>
        </div>
        <div class="pilot-stage-grid">
          <article class="pilot-stage"><div class="pilot-stage-head"><span>01</span><div><p>Evidence intake</p><h2>Import the mission event contract.</h2></div></div>
            <p class="stage-copy">CSV or JSON · 2 MB / 25,000 row maximum · versioned imports · pseudonymous operator keys</p>
            <form class="upload-form" action="/mission-intelligence/pilot/%s/evidence" method="post" enctype="multipart/form-data">
              <input type="hidden" name="csrf_token" value="%s">
              <label class="upload-zone"><input type="file" name="evidence_file" accept=".csv,.json,text/csv,application/json" required><strong>Choose an evidence file</strong><span>run, operator, cohort, assignment, timing, outcome, guardrail</span></label>
              <div class="upload-actions"><a href="/mission-intelligence/pilot/sample.csv">Download sample CSV</a><button class="button button-light" type="submit">Validate &amp; analyze →</button></div>
            </form>%s
          </article>
          <article class="pilot-stage analysis-stage"><div class="pilot-stage-head"><span>02</span><div><p>Transparent analysis</p><h2>Compare the release by cohort.</h2></div></div>%s</article>
        </div>
        <article class="pilot-stage decision-stage"><div class="pilot-stage-head"><span>03</span><div><p>Operator-owned decision</p><h2>Record the release disposition.</h2></div><div class="decision-current"><span>Current record</span><strong>%s</strong></div></div>
          <form action="/mission-intelligence/pilot/%s/decision" method="post">
            <input type="hidden" name="csrf_token" value="%s">
            <div class="decision-actions">%s</div>
            <div class="decision-fields"><label>Decision rationale<textarea name="decision_rationale" required placeholder="State why this evidence supports the selected action.">%s</textarea></label><label>Approved by<input name="approved_by" required value="%s"></label></div>
            <label>Claim boundary<textarea name="claim_boundary" required>%s</textarea></label>
            <div class="decision-footer"><span>HossAgent recommends. The named owner decides.</span><button class="button" type="submit">Sign decision record →</button></div>
          </form>
          %s
        </article>
        %s
      </section>
    """ % (
        html.escape(evaluation.name), html.escape(evaluation.hypothesis), html.escape(evaluation.status.replace("_", " ")), evaluation.evidence_rows, html.escape(revision_line),
        html.escape(evaluation.workflow_name), html.escape(evaluation.release_version), html.escape(evaluation.primary_metric), html.escape(evaluation.primary_direction),
        html.escape(evaluation.guardrail_metric), evaluation.guardrail_threshold, html.escape(evaluation.decision_owner), evaluation.public_id,
        _csrf_token(customer_id, "evidence:%s" % evaluation.public_id),
        _validation_html(validation), _analysis_html(evaluation, analysis), decision_label, evaluation.public_id,
        _csrf_token(customer_id, "decision:%s" % evaluation.public_id), action_options,
        html.escape(evaluation.decision_rationale or ""), html.escape(evaluation.approved_by or evaluation.decision_owner),
        html.escape(evaluation.claim_boundary or (analysis or {}).get("claim_boundary", "This decision applies only to the defined evaluation and imported evidence.")),
        export_actions, _history_html(imports, decisions),
    )


def _render_pilot(
    customer: Customer,
    evaluations: List[MissionEvaluation],
    selected: Optional[MissionEvaluation],
    imports: List[MissionEvidenceImport],
    decisions: List[MissionDecisionRecord],
    notice: str = "",
) -> str:
    with open("templates/mission_pilot.html", "r") as handle:
        template = handle.read()
    evaluation_links = "".join(
        '<a class="%s" href="/mission-intelligence/pilot?evaluation=%s"><span>%s</span><strong>%s</strong><small>%s · %s rows</small></a>' % (
            "active" if selected and selected.id == item.id else "",
            item.public_id,
            html.escape(item.status.replace("_", " ")),
            html.escape(item.name),
            html.escape(item.release_version),
            item.evidence_rows,
        ) for item in evaluations
    ) or '<div class="pilot-list-empty">No evaluations yet.</div>'
    workspace = _evaluation_workspace(selected, imports, decisions, customer.id) if selected else '<section class="pilot-welcome"><p class="eyebrow">Mission Release Gate</p><h1>Run one defensible release decision.</h1><p>Define the release question, import pseudonymous evidence, inspect cohort risk, and leave with a signed release record.</p><ol><li><span>01</span>Define</li><li><span>02</span>Validate</li><li><span>03</span>Decide</li></ol></section>'
    replacements = {
        "%%CUSTOMER%%": html.escape(customer.company),
        "%%CREATE_CSRF%%": _csrf_token(customer.id, "create-evaluation"),
        "%%NOTICE%%": '<div class="pilot-notice">%s</div>' % html.escape(notice) if notice else "",
        "%%EVALUATIONS%%": evaluation_links,
        "%%WORKSPACE%%": workspace,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def pilot_workspace(request: Request, evaluation: Optional[str] = None, notice: str = "", session: Session = Depends(get_session)):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluations = session.exec(select(MissionEvaluation).where(
        MissionEvaluation.customer_id == customer.id
    ).order_by(MissionEvaluation.updated_at.desc())).all()
    selected = None
    if evaluation:
        selected = next((item for item in evaluations if item.public_id == evaluation), None)
    elif evaluations:
        selected = evaluations[0]
    imports: List[MissionEvidenceImport] = []
    decisions: List[MissionDecisionRecord] = []
    if selected:
        imports = list(session.exec(select(MissionEvidenceImport).where(
            MissionEvidenceImport.evaluation_id == selected.id,
            MissionEvidenceImport.customer_id == customer.id,
        ).order_by(MissionEvidenceImport.revision.desc())).all())
        decisions = list(session.exec(select(MissionDecisionRecord).where(
            MissionDecisionRecord.evaluation_id == selected.id,
            MissionDecisionRecord.customer_id == customer.id,
        ).order_by(MissionDecisionRecord.revision.desc())).all())
    return HTMLResponse(_render_pilot(customer, evaluations, selected, imports, decisions, notice))


@router.post("/evaluations")
def create_evaluation(
    request: Request,
    name: str = Form(...),
    workflow_name: str = Form(...),
    hypothesis: str = Form(...),
    release_version: str = Form(...),
    primary_metric: str = Form(...),
    primary_direction: str = Form("lower"),
    outcome_metric: str = Form(...),
    guardrail_metric: str = Form(...),
    guardrail_threshold: float = Form(...),
    decision_owner: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    _require_csrf(customer.id, "create-evaluation", csrf_token)
    if primary_direction not in {"lower", "higher"}:
        primary_direction = "lower"
    guardrail_threshold = max(0.0, min(float(guardrail_threshold), 100.0))
    evaluation = MissionEvaluation(
        customer_id=customer.id,
        public_id=secrets.token_urlsafe(12),
        name=_clean(name, 120),
        workflow_name=_clean(workflow_name, 120),
        hypothesis=_clean(hypothesis, 500),
        release_version=_clean(release_version, 80),
        primary_metric=_clean(primary_metric, 120),
        primary_direction=primary_direction,
        outcome_metric=_clean(outcome_metric, 120),
        guardrail_metric=_clean(guardrail_metric, 120),
        guardrail_threshold=guardrail_threshold,
        decision_owner=_clean(decision_owner, 120),
    )
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return _redirect(evaluation.public_id, "Evaluation configured. Import evidence when the run is ready.")


@router.post("/{public_id}/evidence")
async def import_evidence(
    public_id: str,
    request: Request,
    evidence_file: UploadFile = File(...),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    _require_csrf(customer.id, "evidence:%s" % public_id, csrf_token)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    payload = await evidence_file.read(MAX_UPLOAD_BYTES + 1)
    filename = _clean(evidence_file.filename or "evidence.csv", 180)
    if len(payload) > MAX_UPLOAD_BYTES:
        return _redirect(public_id, "Import blocked: evidence files must be 2 MB or smaller.")
    dataset_sha256 = hashlib.sha256(payload).hexdigest()
    duplicate = session.exec(select(MissionEvidenceImport).where(
        MissionEvidenceImport.evaluation_id == evaluation.id,
        MissionEvidenceImport.customer_id == customer.id,
        MissionEvidenceImport.dataset_sha256 == dataset_sha256,
        MissionEvidenceImport.valid == True,  # noqa: E712
    )).first()
    if duplicate:
        return _redirect(public_id, "This exact evidence file is already recorded as revision %s." % duplicate.revision)

    latest_import = session.exec(select(MissionEvidenceImport).where(
        MissionEvidenceImport.evaluation_id == evaluation.id,
        MissionEvidenceImport.customer_id == customer.id,
    ).order_by(MissionEvidenceImport.revision.desc())).first()
    revision = (latest_import.revision if latest_import else 0) + 1
    content_type = _clean((evidence_file.content_type or "").split(";", 1)[0].lower(), 100)
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    try:
        if suffix not in ALLOWED_EVIDENCE_SUFFIXES or content_type not in ALLOWED_EVIDENCE_CONTENT_TYPES:
            raise ValueError("Evidence files must be CSV or JSON.")
        records = parse_evidence_bytes(filename, payload)
        normalized, validation = validate_evidence_records(records)
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        normalized = []
        validation = {"valid": False, "rows_received": 0, "rows_valid": 0, "completeness_pct": 0, "errors": [str(exc)], "warnings": []}

    analysis = None
    if validation.get("valid"):
        analysis = compute_evidence_analysis(normalized, evaluation.guardrail_threshold, evaluation.primary_direction)
    evidence_import = MissionEvidenceImport(
        customer_id=customer.id,
        evaluation_id=evaluation.id,
        revision=revision,
        filename=filename,
        content_type=content_type or None,
        bytes_received=len(payload),
        dataset_sha256=dataset_sha256,
        row_count=len(normalized),
        operator_count=len({row["operator_id"] for row in normalized}),
        valid=bool(validation.get("valid")),
        validation_json=json.dumps(validation, sort_keys=True),
        analysis_json=json.dumps(analysis, sort_keys=True) if analysis else None,
        imported_by=customer.contact_email,
    )
    session.add(evidence_import)
    session.flush()
    evaluation.evidence_revision = revision
    evaluation.updated_at = datetime.utcnow()

    if not validation.get("valid"):
        session.add(evaluation)
        session.commit()
        return _redirect(public_id, "Import revision %s was blocked. The active evidence record was not changed." % revision)

    for row in normalized:
        session.add(MissionEvidenceEvent(evaluation_id=evaluation.id, import_id=evidence_import.id, **row))
    evaluation.active_import_id = evidence_import.id
    evaluation.dataset_filename = filename
    evaluation.dataset_sha256 = dataset_sha256
    evaluation.validation_json = evidence_import.validation_json
    evaluation.analysis_json = evidence_import.analysis_json
    evaluation.analysis_version = analysis["analysis_version"]
    evaluation.evidence_rows = len(normalized)
    evaluation.decision_action = None
    evaluation.decision_rationale = None
    evaluation.approved_by = None
    evaluation.claim_boundary = None
    evaluation.decided_at = None
    evaluation.status = "review_required"
    session.add(evaluation)
    session.commit()
    return _redirect(public_id, "Evidence revision %s accepted. Cohort analysis and release recommendation are ready." % revision)


@router.post("/{public_id}/decision")
def record_decision(
    public_id: str,
    request: Request,
    decision_action: str = Form(...),
    decision_rationale: str = Form(...),
    approved_by: str = Form(...),
    claim_boundary: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    _require_csrf(customer.id, "decision:%s" % public_id, csrf_token)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    if not evaluation.analysis_json:
        return _redirect(public_id, "Import valid evidence before recording a decision.")
    if decision_action not in DECISION_ACTIONS:
        return _redirect(public_id, "Select a valid release action.")
    evidence_import = _active_import(session, evaluation)
    if not evidence_import or not evidence_import.analysis_json:
        return _redirect(public_id, "The active evidence revision is unavailable. Import evidence again before signing.")
    rationale = _clean(decision_rationale, 2000)
    approver = _clean(approved_by, 120)
    boundary = _clean(claim_boundary, 1200)
    if not rationale or not approver or not boundary:
        return _redirect(public_id, "Rationale, approver, and claim boundary are required.")
    latest_decision = session.exec(select(MissionDecisionRecord).where(
        MissionDecisionRecord.evaluation_id == evaluation.id,
        MissionDecisionRecord.customer_id == customer.id,
    ).order_by(MissionDecisionRecord.revision.desc())).first()
    if latest_decision and latest_decision.import_id == evidence_import.id and all((
        latest_decision.action == decision_action,
        latest_decision.rationale == rationale,
        latest_decision.approved_by == approver,
        latest_decision.claim_boundary == boundary,
    )):
        return _redirect(public_id, "That signed disposition is already the current decision record.")
    revision = (latest_decision.revision if latest_decision else 0) + 1
    signed_at = datetime.utcnow()
    record_sha256 = build_decision_fingerprint(
        evaluation, evidence_import, revision, decision_action, rationale, approver, boundary, signed_at
    )
    analysis = json.loads(evidence_import.analysis_json)
    decision_record = MissionDecisionRecord(
        customer_id=customer.id,
        evaluation_id=evaluation.id,
        import_id=evidence_import.id,
        evidence_revision=evidence_import.revision,
        revision=revision,
        action=decision_action,
        rationale=rationale,
        approved_by=approver,
        claim_boundary=boundary,
        system_recommendation=analysis.get("recommendation", {}).get("action", ""),
        analysis_version=analysis.get("analysis_version", evaluation.analysis_version),
        dataset_sha256=evidence_import.dataset_sha256,
        record_sha256=record_sha256,
        signed_at=signed_at,
    )
    session.add(decision_record)
    evaluation.decision_action = decision_action
    evaluation.decision_rationale = rationale
    evaluation.approved_by = approver
    evaluation.claim_boundary = boundary
    evaluation.decided_at = signed_at
    evaluation.decision_revision = revision
    evaluation.updated_at = datetime.utcnow()
    evaluation.status = "decided"
    session.add(evaluation)
    session.commit()
    return _redirect(public_id, "Decision revision %s signed. The release record is ready to export." % revision)


def _brief_html(evaluation: MissionEvaluation, customer: Customer, decision_record: MissionDecisionRecord) -> str:
    analysis = json.loads(evaluation.analysis_json)
    recommendation = analysis["recommendation"]
    cohort_rows = "".join(
        "<tr><td>%s</td><td>%s / %s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(row["name"]), row["control"]["count"], row["treatment"]["count"],
            _format_number(row["treatment"]["median_seconds"], "s"),
            _format_number(row["treatment"]["outcome_rate"], "%"),
            _format_number(row["treatment"]["guardrail_rate"], "%"),
        ) for row in analysis["cohorts"]
    )
    decision = _action_label(decision_record.action)
    decided_at = decision_record.signed_at.isoformat() + "Z"
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>%s · Release record</title><style>
      body{margin:0;background:#eeece4;color:#171a18;font:15px/1.55 Inter,Arial,sans-serif}.page{max-width:920px;margin:40px auto;background:#fffefa;border:1px solid #c9c8c0}.head{padding:32px;background:#111513;color:#fff}.brand{color:#c8f16b;font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:12px}.head h1{font-size:42px;line-height:1;margin:26px 0 10px}.head p{color:#a9b1ab}.meta,.metrics{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #c9c8c0}.meta div,.metrics div{min-width:0;padding:18px;border-right:1px solid #c9c8c0}.meta span,.metrics span{display:block;color:#626963;font-size:11px;text-transform:uppercase}.meta strong,.metrics strong{display:block;margin-top:6px;overflow-wrap:anywhere}.section{padding:28px 32px;border-bottom:1px solid #c9c8c0}.decision{border-left:5px solid #c8f16b;background:#edf4ef}.decision strong{font-size:28px}.decision p{max-width:760px}.section h2{margin-top:0}table{width:100%%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}.boundary{background:#f6efe3;border-left:4px solid #d19b48}.foot{padding:22px 32px;color:#626963;font-size:12px;overflow-wrap:anywhere}.actions{max-width:920px;margin:20px auto;display:flex;gap:10px}.actions button,.actions a{padding:11px 16px;background:#111513;color:#fff;text-decoration:none;border:0;border-radius:5px;cursor:pointer}@media(max-width:700px){.meta,.metrics{grid-template-columns:1fr 1fr}.head h1{font-size:32px}.page{margin:0}.section{padding:22px 18px}}@media print{.actions{display:none}.page{margin:0;border:0}}
    </style></head><body><div class="actions"><button onclick="window.print()">Print / save PDF</button><a href="/mission-intelligence/pilot/%s/brief.pdf">Download PDF</a></div><main class="page">
      <header class="head"><div class="brand">HossAgent · Mission Release Gate</div><h1>%s</h1><p>%s</p></header>
      <section class="meta"><div><span>Customer</span><strong>%s</strong></div><div><span>Release</span><strong>%s</strong></div><div><span>Evidence / decision</span><strong>E%s / D%s</strong></div><div><span>Analysis</span><strong>%s</strong></div></section>
      <section class="section decision"><span>Signed disposition</span><br><strong>%s</strong><p>%s</p><small>Approved by %s · %s</small></section>
      <section class="metrics"><div><span>Eligible runs</span><strong>%s</strong></div><div><span>Operators</span><strong>%s</strong></div><div><span>System recommendation</span><strong>%s</strong></div><div><span>Guardrail threshold</span><strong>%.1f%%</strong></div></section>
      <section class="section"><h2>Cohort evidence</h2><table><thead><tr><th>Cohort</th><th>Control / treatment</th><th>Treatment median</th><th>Outcome</th><th>Guardrail</th></tr></thead><tbody>%s</tbody></table></section>
      <section class="section"><h2>Recommendation basis</h2><p><strong>%s</strong></p><p>%s</p></section>
      <section class="section boundary"><h2>Claim boundary</h2><p>%s</p></section>
      <footer class="foot">Dataset SHA-256: %s<br>Decision SHA-256: %s<br>Source: %s · Generated %s</footer>
    </main></body></html>""" % (
        html.escape(evaluation.name), evaluation.public_id, html.escape(evaluation.name), html.escape(evaluation.hypothesis),
        html.escape(customer.company), html.escape(evaluation.release_version), decision_record.evidence_revision, decision_record.revision,
        html.escape(evaluation.analysis_version), decision,
        html.escape(decision_record.rationale), html.escape(decision_record.approved_by), decided_at,
        analysis["row_count"], analysis["operator_count"], html.escape(_action_label(recommendation["action"])),
        evaluation.guardrail_threshold, cohort_rows, html.escape(recommendation["title"]), html.escape(recommendation["basis"]),
        html.escape(decision_record.claim_boundary), html.escape(decision_record.dataset_sha256), html.escape(decision_record.record_sha256),
        html.escape(evaluation.dataset_filename or "unavailable"), datetime.utcnow().isoformat() + "Z",
    )


@router.get("/{public_id}/brief", response_class=HTMLResponse)
def evidence_brief(public_id: str, request: Request, session: Session = Depends(get_session)):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    decision_record = _current_decision(session, evaluation)
    if not decision_record or not evaluation.analysis_json:
        raise HTTPException(status_code=409, detail="Sign a decision for the active evidence revision before exporting")
    return HTMLResponse(_brief_html(evaluation, customer, decision_record))


@router.get("/{public_id}/brief.pdf")
def evidence_brief_pdf(public_id: str, request: Request, session: Session = Depends(get_session)):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    decision_record = _current_decision(session, evaluation)
    if not decision_record or not evaluation.analysis_json:
        raise HTTPException(status_code=409, detail="Sign a decision for the active evidence revision before exporting")
    analysis = json.loads(evaluation.analysis_json)
    recommendation = analysis["recommendation"]
    from fpdf import FPDF

    def latin(value: Any) -> str:
        return str(value or "").encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_title(latin(evaluation.name + " - Release record"))
    pdf.add_page()
    pdf.set_fill_color(17, 21, 19)
    pdf.rect(0, 0, 210, 54, "F")
    pdf.set_text_color(200, 241, 107)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(16, 13)
    pdf.cell(0, 6, "HOSSAGENT / MISSION RELEASE GATE")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(16, 25)
    pdf.multi_cell(178, 9, latin(evaluation.name))
    pdf.set_text_color(23, 26, 24)
    pdf.set_xy(16, 64)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(178, 6, latin(evaluation.hypothesis))
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "RECORDED DISPOSITION")
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 9, latin(_action_label(decision_record.action)))
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(178, 6, latin(decision_record.rationale))
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "EVIDENCE SUMMARY")
    pdf.ln(9)
    overall = analysis["cohorts"][0]
    treatment = overall["treatment"]
    lines = [
        "Eligible runs: %s | Pseudonymous operators: %s" % (analysis["row_count"], analysis["operator_count"]),
        "Treatment median: %s | Outcome success: %s" % (_format_number(treatment["median_seconds"], "s"), _format_number(treatment["outcome_rate"], "%")),
        "Guardrail rate: %s | Threshold: %.1f%%" % (_format_number(treatment["guardrail_rate"], "%"), evaluation.guardrail_threshold),
        "System recommendation: %s" % _action_label(recommendation["action"]),
    ]
    pdf.set_font("Helvetica", "", 10)
    for line in lines:
        pdf.multi_cell(178, 7, latin(line), border="B")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "CLAIM BOUNDARY")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(178, 6, latin(decision_record.claim_boundary))
    pdf.ln(5)
    pdf.set_text_color(98, 105, 99)
    pdf.multi_cell(178, 5, latin("Release %s | Evidence E%s | Decision D%s | Analysis %s | Approved by %s" % (
        evaluation.release_version, decision_record.evidence_revision, decision_record.revision, evaluation.analysis_version, decision_record.approved_by
    )))
    pdf.multi_cell(178, 5, latin("Dataset SHA-256: %s\nDecision SHA-256: %s" % (
        decision_record.dataset_sha256, decision_record.record_sha256
    )))
    content = bytes(pdf.output())
    filename = "%s-release-record.pdf" % _slug(evaluation.name)
    return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="%s"' % filename})


@router.get("/sample.csv")
def sample_evidence_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["run_id", "operator_id", "cohort", "variant", "workflow_seconds", "outcome_success", "guardrail_triggered", "event_time"])
    sequence = 1
    for cohort in ("Certified", "Trainee"):
        for variant in ("control", "treatment"):
            for index in range(1, 9):
                if cohort == "Certified":
                    seconds = (48 - index) if variant == "control" else (37 - index / 2)
                    outcome = not (variant == "control" and index == 2)
                    guardrail = index == 8 and variant == "control"
                else:
                    seconds = (68 - index) if variant == "control" else (58 - index / 2)
                    outcome = index not in ({2, 7} if variant == "control" else {3, 6})
                    guardrail = variant == "treatment" and index in {2, 4, 6}
                writer.writerow([
                    "RUN-%03d" % sequence,
                    "%s-%02d" % (cohort[:3].upper(), index),
                    cohort,
                    variant,
                    round(seconds, 1),
                    str(outcome).lower(),
                    str(guardrail).lower(),
                    "2026-08-07T14:%02d:00Z" % (sequence % 60),
                ])
                sequence += 1
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="hossagent-mission-evidence-sample.csv"'},
    )
