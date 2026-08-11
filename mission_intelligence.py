"""Pilot workflow for HossAgent Mission Intelligence."""

import csv
import hashlib
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
from sqlmodel import Session, delete, select

from auth_utils import SESSION_COOKIE_NAME, get_customer_from_session
from database import get_session
from models import Customer, MissionEvaluation, MissionEvidenceEvent


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


def _clean(value: Any, limit: int = 240) -> str:
    return str(value or "").strip()[:limit]


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "evaluation"


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
    if suffix == "json" or text.lstrip().startswith(("[", "{")):
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


def _evaluation_workspace(evaluation: MissionEvaluation) -> str:
    validation = json.loads(evaluation.validation_json) if evaluation.validation_json else None
    analysis = json.loads(evaluation.analysis_json) if evaluation.analysis_json else None
    decision_label = (evaluation.decision_action or "Not recorded").replace("_", " ").title()
    checked = evaluation.decision_action or (analysis or {}).get("recommendation", {}).get("action", "modify")
    action_options = "".join(
        '<label><input type="radio" name="decision_action" value="%s" %s><span>%s</span></label>' % (
            action, "checked" if checked == action else "", label
        ) for action, label in (("expand", "Expand"), ("modify", "Modify"), ("stop", "Stop"), ("collect_more", "Collect more"))
    )
    return """
      <section class="pilot-workspace">
        <div class="pilot-workspace-head"><div><p class="eyebrow">Active evaluation</p><h1>%s</h1><p>%s</p></div><div class="pilot-status"><span>%s</span><strong>%s</strong></div></div>
        <div class="pilot-definition">
          <div><span>Workflow</span><strong>%s</strong></div><div><span>Release</span><strong>%s</strong></div><div><span>Primary measure</span><strong>%s · %s is better</strong></div><div><span>Guardrail</span><strong>%s ≤ %.1f%%</strong></div><div><span>Decision owner</span><strong>%s</strong></div>
        </div>
        <div class="pilot-stage-grid">
          <article class="pilot-stage"><div class="pilot-stage-head"><span>01</span><div><p>Evidence intake</p><h2>Import the mission event contract.</h2></div></div>
            <p class="stage-copy">CSV or JSON · 2 MB maximum · replacement import · pseudonymous operator keys</p>
            <form class="upload-form" action="/mission-intelligence/pilot/%s/evidence" method="post" enctype="multipart/form-data">
              <label class="upload-zone"><input type="file" name="evidence_file" accept=".csv,.json,text/csv,application/json" required><strong>Choose an evidence file</strong><span>run, operator, cohort, assignment, timing, outcome, guardrail</span></label>
              <div class="upload-actions"><a href="/mission-intelligence/pilot/sample.csv">Download sample CSV</a><button class="button button-light" type="submit">Validate &amp; analyze →</button></div>
            </form>%s
          </article>
          <article class="pilot-stage analysis-stage"><div class="pilot-stage-head"><span>02</span><div><p>Transparent analysis</p><h2>Compare the release by cohort.</h2></div></div>%s</article>
        </div>
        <article class="pilot-stage decision-stage"><div class="pilot-stage-head"><span>03</span><div><p>Operator-owned decision</p><h2>Record the release disposition.</h2></div><div class="decision-current"><span>Current record</span><strong>%s</strong></div></div>
          <form action="/mission-intelligence/pilot/%s/decision" method="post">
            <div class="decision-actions">%s</div>
            <div class="decision-fields"><label>Decision rationale<textarea name="decision_rationale" required placeholder="State why this evidence supports the selected action.">%s</textarea></label><label>Approved by<input name="approved_by" required value="%s"></label></div>
            <label>Claim boundary<textarea name="claim_boundary" required>%s</textarea></label>
            <div class="decision-footer"><span>HossAgent recommends. The named owner decides.</span><button class="button" type="submit">Sign decision record →</button></div>
          </form>
          <div class="export-actions"><a href="/mission-intelligence/pilot/%s/brief" target="_blank">Open HTML brief</a><a href="/mission-intelligence/pilot/%s/brief.pdf">Download PDF brief</a></div>
        </article>
      </section>
    """ % (
        html.escape(evaluation.name), html.escape(evaluation.hypothesis), html.escape(evaluation.status.replace("_", " ")), evaluation.evidence_rows,
        html.escape(evaluation.workflow_name), html.escape(evaluation.release_version), html.escape(evaluation.primary_metric), html.escape(evaluation.primary_direction),
        html.escape(evaluation.guardrail_metric), evaluation.guardrail_threshold, html.escape(evaluation.decision_owner), evaluation.public_id,
        _validation_html(validation), _analysis_html(evaluation, analysis), decision_label, evaluation.public_id, action_options,
        html.escape(evaluation.decision_rationale or ""), html.escape(evaluation.approved_by or evaluation.decision_owner),
        html.escape(evaluation.claim_boundary or (analysis or {}).get("claim_boundary", "This decision applies only to the defined evaluation and imported evidence.")),
        evaluation.public_id, evaluation.public_id,
    )


def _render_pilot(customer: Customer, evaluations: List[MissionEvaluation], selected: Optional[MissionEvaluation], notice: str = "") -> str:
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
    workspace = _evaluation_workspace(selected) if selected else '<section class="pilot-welcome"><p class="eyebrow">Pilot workspace</p><h1>Run one defensible release decision.</h1><p>Define the question, import pseudonymous exercise evidence, inspect cohort risk, and leave with a signed decision artifact.</p><ol><li><span>01</span>Define</li><li><span>02</span>Import</li><li><span>03</span>Decide</li></ol></section>'
    replacements = {
        "%%CUSTOMER%%": html.escape(customer.company),
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
    return HTMLResponse(_render_pilot(customer, evaluations, selected, notice))


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
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
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
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    payload = await evidence_file.read(MAX_UPLOAD_BYTES + 1)
    filename = _clean(evidence_file.filename or "evidence.csv", 180)
    if len(payload) > MAX_UPLOAD_BYTES:
        return _redirect(public_id, "Import blocked: evidence files must be 2 MB or smaller.")
    try:
        records = parse_evidence_bytes(filename, payload)
        normalized, validation = validate_evidence_records(records)
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        normalized = []
        validation = {"valid": False, "rows_received": 0, "rows_valid": 0, "completeness_pct": 0, "errors": [str(exc)], "warnings": []}

    evaluation.dataset_filename = filename
    evaluation.dataset_sha256 = hashlib.sha256(payload).hexdigest()
    evaluation.validation_json = json.dumps(validation)
    evaluation.updated_at = datetime.utcnow()
    if not validation.get("valid"):
        evaluation.status = "validation_failed"
        session.add(evaluation)
        session.commit()
        return _redirect(public_id, "Import blocked. Review the evidence contract findings below.")

    session.exec(delete(MissionEvidenceEvent).where(MissionEvidenceEvent.evaluation_id == evaluation.id))
    for row in normalized:
        session.add(MissionEvidenceEvent(evaluation_id=evaluation.id, **row))
    analysis = compute_evidence_analysis(normalized, evaluation.guardrail_threshold, evaluation.primary_direction)
    evaluation.analysis_json = json.dumps(analysis)
    evaluation.evidence_rows = len(normalized)
    evaluation.status = "review_required"
    session.add(evaluation)
    session.commit()
    return _redirect(public_id, "Evidence accepted. Cohort analysis and release recommendation are ready.")


@router.post("/{public_id}/decision")
def record_decision(
    public_id: str,
    request: Request,
    decision_action: str = Form(...),
    decision_rationale: str = Form(...),
    approved_by: str = Form(...),
    claim_boundary: str = Form(...),
    session: Session = Depends(get_session),
):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    if not evaluation.analysis_json:
        return _redirect(public_id, "Import valid evidence before recording a decision.")
    if decision_action not in DECISION_ACTIONS:
        return _redirect(public_id, "Select a valid release action.")
    evaluation.decision_action = decision_action
    evaluation.decision_rationale = _clean(decision_rationale, 2000)
    evaluation.approved_by = _clean(approved_by, 120)
    evaluation.claim_boundary = _clean(claim_boundary, 1200)
    evaluation.decided_at = datetime.utcnow()
    evaluation.updated_at = datetime.utcnow()
    evaluation.status = "decided"
    session.add(evaluation)
    session.commit()
    return _redirect(public_id, "Decision signed. The evidence brief is ready to export.")


def _brief_html(evaluation: MissionEvaluation, customer: Customer) -> str:
    if not evaluation.analysis_json:
        raise HTTPException(status_code=409, detail="Evidence analysis is not ready")
    analysis = json.loads(evaluation.analysis_json)
    recommendation = analysis["recommendation"]
    overall = analysis["cohorts"][0]
    cohort_rows = "".join(
        "<tr><td>%s</td><td>%s / %s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            html.escape(row["name"]), row["control"]["count"], row["treatment"]["count"],
            _format_number(row["treatment"]["median_seconds"], "s"),
            _format_number(row["treatment"]["outcome_rate"], "%"),
            _format_number(row["treatment"]["guardrail_rate"], "%"),
        ) for row in analysis["cohorts"]
    )
    decision = (evaluation.decision_action or "Pending operator decision").replace("_", " ").upper()
    decided_at = evaluation.decided_at.isoformat() + "Z" if evaluation.decided_at else "Not yet signed"
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>%s · Evidence brief</title><style>
      body{margin:0;background:#eeece4;color:#171a18;font:15px/1.55 Inter,Arial,sans-serif}.page{max-width:920px;margin:40px auto;background:#fffefa;border:1px solid #c9c8c0}.head{padding:32px;background:#111513;color:#fff}.brand{color:#c8f16b;font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:12px}.head h1{font-size:42px;line-height:1;margin:26px 0 10px}.head p{color:#a9b1ab}.meta,.metrics{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #c9c8c0}.meta div,.metrics div{padding:18px;border-right:1px solid #c9c8c0}.meta span,.metrics span{display:block;color:#626963;font-size:11px;text-transform:uppercase}.meta strong,.metrics strong{display:block;margin-top:6px}.section{padding:28px 32px;border-bottom:1px solid #c9c8c0}.decision{border-left:5px solid #c8f16b;background:#edf4ef}.decision strong{font-size:28px}.decision p{max-width:760px}.section h2{margin-top:0}table{width:100%%;border-collapse:collapse}th,td{text-align:left;padding:10px;border-bottom:1px solid #ddd}.boundary{background:#f6efe3;border-left:4px solid #d19b48}.foot{padding:22px 32px;color:#626963;font-size:12px}.actions{max-width:920px;margin:20px auto;display:flex;gap:10px}.actions button,.actions a{padding:11px 16px;background:#111513;color:#fff;text-decoration:none;border:0;border-radius:5px;cursor:pointer}@media print{.actions{display:none}.page{margin:0;border:0}}
    </style></head><body><div class="actions"><button onclick="window.print()">Print / save PDF</button><a href="/mission-intelligence/pilot/%s/brief.pdf">Download PDF</a></div><main class="page">
      <header class="head"><div class="brand">HossAgent · Mission Intelligence</div><h1>%s</h1><p>%s</p></header>
      <section class="meta"><div><span>Customer</span><strong>%s</strong></div><div><span>Release</span><strong>%s</strong></div><div><span>Analysis</span><strong>%s</strong></div><div><span>Dataset SHA-256</span><strong>%s…</strong></div></section>
      <section class="section decision"><span>Recorded disposition</span><br><strong>%s</strong><p>%s</p><small>Approved by %s · %s</small></section>
      <section class="metrics"><div><span>Eligible runs</span><strong>%s</strong></div><div><span>Operators</span><strong>%s</strong></div><div><span>System recommendation</span><strong>%s</strong></div><div><span>Guardrail threshold</span><strong>%.1f%%</strong></div></section>
      <section class="section"><h2>Cohort evidence</h2><table><thead><tr><th>Cohort</th><th>Control / treatment</th><th>Treatment median</th><th>Outcome</th><th>Guardrail</th></tr></thead><tbody>%s</tbody></table></section>
      <section class="section"><h2>Recommendation basis</h2><p><strong>%s</strong></p><p>%s</p></section>
      <section class="section boundary"><h2>Claim boundary</h2><p>%s</p></section>
      <footer class="foot">Locally generated evidence artifact · %s · Source file: %s</footer>
    </main></body></html>""" % (
        html.escape(evaluation.name), evaluation.public_id, html.escape(evaluation.name), html.escape(evaluation.hypothesis),
        html.escape(customer.company), html.escape(evaluation.release_version), html.escape(evaluation.analysis_version),
        html.escape((evaluation.dataset_sha256 or "unavailable")[:16]), decision,
        html.escape(evaluation.decision_rationale or "Operator decision has not been recorded."),
        html.escape(evaluation.approved_by or evaluation.decision_owner), decided_at,
        analysis["row_count"], analysis["operator_count"], html.escape(recommendation["action"].replace("_", " ").title()),
        evaluation.guardrail_threshold, cohort_rows, html.escape(recommendation["title"]), html.escape(recommendation["basis"]),
        html.escape(evaluation.claim_boundary or analysis["claim_boundary"]), datetime.utcnow().isoformat() + "Z", html.escape(evaluation.dataset_filename or "unavailable"),
    )


@router.get("/{public_id}/brief", response_class=HTMLResponse)
def evidence_brief(public_id: str, request: Request, session: Session = Depends(get_session)):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    return HTMLResponse(_brief_html(evaluation, customer))


@router.get("/{public_id}/brief.pdf")
def evidence_brief_pdf(public_id: str, request: Request, session: Session = Depends(get_session)):
    customer = _customer(request, session)
    if not customer:
        return RedirectResponse(url="/login?next=/mission-intelligence/pilot", status_code=303)
    evaluation = _owned_evaluation(session, customer.id, public_id)
    if not evaluation.analysis_json:
        raise HTTPException(status_code=409, detail="Evidence analysis is not ready")
    analysis = json.loads(evaluation.analysis_json)
    recommendation = analysis["recommendation"]
    from fpdf import FPDF

    def latin(value: Any) -> str:
        return str(value or "").encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_title(latin(evaluation.name + " - Evidence brief"))
    pdf.add_page()
    pdf.set_fill_color(17, 21, 19)
    pdf.rect(0, 0, 210, 54, "F")
    pdf.set_text_color(200, 241, 107)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(16, 13)
    pdf.cell(0, 6, "HOSSAGENT / MISSION INTELLIGENCE")
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
    pdf.cell(0, 9, latin((evaluation.decision_action or "Pending").replace("_", " ").upper()))
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(178, 6, latin(evaluation.decision_rationale or "Operator decision has not been recorded."))
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
        "System recommendation: %s" % recommendation["title"],
    ]
    pdf.set_font("Helvetica", "", 10)
    for line in lines:
        pdf.multi_cell(178, 7, latin(line), border="B")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "CLAIM BOUNDARY")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(178, 6, latin(evaluation.claim_boundary or analysis["claim_boundary"]))
    pdf.ln(5)
    pdf.set_text_color(98, 105, 99)
    pdf.multi_cell(178, 5, latin("Release %s | Analysis %s | Dataset %s | Approved by %s" % (
        evaluation.release_version, evaluation.analysis_version, (evaluation.dataset_sha256 or "unavailable")[:20], evaluation.approved_by or evaluation.decision_owner
    )))
    content = bytes(pdf.output())
    filename = "%s-evidence-brief.pdf" % _slug(evaluation.name)
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
