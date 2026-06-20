from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlmodel import Session, select, func

from models import LeadEvent, Signal, PendingOutbound, Report, Company, Lead, Customer


VISIBLE_STATUSES = {"ENRICHED_NO_OUTBOUND", "OUTBOUND_SENT", "SKIPPED"}


def _parse_json(text: Optional[str]) -> Dict[str, Any]:
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except Exception:
        return {}


def _opportunity_allowed(event: LeadEvent) -> bool:
    return (event.enrichment_status or "").upper() in VISIBLE_STATUSES


def list_customer_opportunities(
    session: Session,
    customer_id: int,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    filters = filters or {}
    query = select(LeadEvent).where(LeadEvent.company_id == customer_id)
    query = query.order_by(LeadEvent.urgency_score.desc(), LeadEvent.created_at.desc())
    events = session.exec(query).all()
    items: List[Dict[str, Any]] = []

    for event in events:
        if not _opportunity_allowed(event):
            continue
        if filters.get("status") and (event.enrichment_status or "") != filters["status"]:
            continue
        if filters.get("signal_type") and (event.category or "").lower() != filters["signal_type"].lower():
            continue
        if filters.get("geography") and filters["geography"].lower() not in (event.lead_company or "").lower() and filters["geography"].lower() not in (event.enriched_company_name or "").lower() and filters["geography"].lower() not in (event.lead_domain or "").lower():
            continue
        if filters.get("high_urgency") and event.urgency_score < 75:
            continue

        signal = session.exec(select(Signal).where(Signal.id == event.signal_id)).first() if event.signal_id else None
        outbound = session.exec(
            select(PendingOutbound).where(PendingOutbound.lead_event_id == event.id).order_by(PendingOutbound.created_at.desc()).limit(1)
        ).first()
        company = session.exec(select(Company).where(Company.id == event.company_table_id)).first() if event.company_table_id else None
        lead = session.exec(select(Lead).where(Lead.id == event.lead_id)).first() if event.lead_id else None
        items.append(build_opportunity_detail(event, signal=signal, outbound=outbound, company=company, lead=lead))
        if len(items) >= limit:
            break
    return items


def get_opportunity_detail(session: Session, opportunity_id: int, customer_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    query = select(LeadEvent).where(LeadEvent.id == opportunity_id)
    if customer_id:
        query = query.where(LeadEvent.company_id == customer_id)
    event = session.exec(query).first()
    if not event:
        return None
    signal = session.exec(select(Signal).where(Signal.id == event.signal_id)).first() if event.signal_id else None
    outbound = session.exec(select(PendingOutbound).where(PendingOutbound.lead_event_id == event.id).order_by(PendingOutbound.created_at.desc()).limit(1)).first()
    company = session.exec(select(Company).where(Company.id == event.company_table_id)).first() if event.company_table_id else None
    lead = session.exec(select(Lead).where(Lead.id == event.lead_id)).first() if event.lead_id else None
    reports = session.exec(select(Report).where(Report.lead_event_id == event.id).order_by(Report.created_at.desc())).all()
    return build_opportunity_detail(event, signal=signal, outbound=outbound, company=company, lead=lead, reports=reports)


def list_ready_opportunities(session: Session, customer_id: int) -> List[Dict[str, Any]]:
    return [item for item in list_customer_opportunities(session, customer_id, limit=100) if item.get("enrichment_status") in VISIBLE_STATUSES]


def build_opportunity_detail(
    event: LeadEvent,
    signal: Optional[Signal] = None,
    outbound: Optional[PendingOutbound] = None,
    company: Optional[Company] = None,
    lead: Optional[Lead] = None,
    reports: Optional[List[Report]] = None,
) -> Dict[str, Any]:
    signal_payload = _parse_json(signal.raw_payload if signal else None)
    extracted = _parse_json(signal.extracted_contact_info if signal else None)
    mission_log = _parse_json(event.enrichment_mission_log) if event.enrichment_mission_log else {}
    if not isinstance(mission_log, dict):
        mission_log = {"entries": mission_log}
    return {
        "id": event.id,
        "company_name": event.lead_company or event.enriched_company_name or (company.name if company else None) or "Unknown Company",
        "company": company,
        "lead": lead,
        "signal": signal,
        "signal_type": signal.source_type if signal else event.category,
        "signal_source": signal.source_type if signal else None,
        "raw_signal_excerpt": (signal.context_summary or "")[:300] if signal else (event.summary or "")[:300],
        "signal_payload": signal_payload,
        "extracted_facts": extracted,
        "geography": signal.geography if signal and signal.geography else None,
        "baseline_reasoning": event.recommended_action or event.last_contact_summary or "",
        "why_now": event.summary,
        "second_order_effects": event.last_contact_summary or "",
        "recommended_angle": event.recommended_action or "",
        "urgency_score": event.urgency_score,
        "confidence_score": round(((event.domain_confidence or 0) + (event.email_confidence or 0) + (event.phone_confidence or 0)) / 3 * 100, 1),
        "enrichment_status": event.enrichment_status,
        "domain_confidence": event.domain_confidence,
        "email_confidence": event.email_confidence,
        "phone_confidence": event.phone_confidence,
        "mission_log": mission_log.get("entries") or mission_log.get("mission_log") or [],
        "outbound": outbound,
        "outbound_subject": outbound.subject if outbound else event.outbound_subject,
        "outbound_body": outbound.body if outbound else event.outbound_message,
        "outbound_status": outbound.status if outbound else None,
        "reports": reports or [],
        "status": event.status,
        "created_at": event.created_at,
        "location": signal.geography if signal else event.enriched_company_name,
        "raw_excerpt": signal.context_summary if signal else event.summary,
    }


def get_admin_metrics(session: Session) -> Dict[str, Any]:
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    total_customers = session.exec(select(func.count(Customer.id))).one()
    signals_today = session.exec(select(func.count(Signal.id)).where(Signal.created_at >= today_start)).one()
    lead_events = session.exec(select(func.count(LeadEvent.id))).one()
    leads_created = session.exec(select(func.count(Lead.id))).one()
    outbound_drafts = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "PENDING")).one()
    emails_sent = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "SENT")).one()
    enrichment_rate = session.exec(select(func.avg(LeadEvent.domain_confidence))).one() or 0
    high_urgency = session.exec(select(func.count(LeadEvent.id)).where(LeadEvent.urgency_score >= 75)).one()
    error_rate = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "FAILED")).one()
    return {
        "active_customers": total_customers,
        "signals_ingested": signals_today,
        "leads_created": leads_created,
        "enrichment_rate": round(float(enrichment_rate or 0) * 100, 1),
        "outbound_drafts": outbound_drafts,
        "emails_sent": emails_sent,
        "error_rate": error_rate,
        "opportunity_synthesis_rate": round((lead_events / signals_today * 100), 1) if signals_today else 0,
        "hmx_reachability_delta": round((high_urgency - outbound_drafts), 1),
    }
