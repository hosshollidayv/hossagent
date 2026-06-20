from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlmodel import Session, select, func

from models import Customer, Signal, LeadEvent, PendingOutbound, Message, SupportTicket


def get_admin_metrics(session: Session) -> Dict[str, Any]:
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_customers = session.exec(select(func.count(Customer.id))).one()
    signals_ingested = session.exec(select(func.count(Signal.id)).where(Signal.created_at >= today_start)).one()
    leads_created = session.exec(select(func.count(LeadEvent.id))).one()
    outbound_drafts = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "PENDING")).one()
    emails_sent = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "SENT")).one()
    errors = session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status == "FAILED")).one()
    enrichment_rate = session.exec(select(func.avg(LeadEvent.domain_confidence))).one() or 0.0
    hmx_delta = session.exec(select(func.avg(LeadEvent.email_confidence))).one() or 0.0
    opportunity_rate = session.exec(select(func.count(LeadEvent.id)).where(LeadEvent.enrichment_status.in_(["ENRICHED_NO_OUTBOUND", "OUTBOUND_SENT"]))).one()
    total_signals = session.exec(select(func.count(Signal.id))).one() or 1
    return {
        "active_customers": active_customers,
        "signals_ingested": signals_ingested,
        "leads_created": leads_created,
        "enrichment_rate": round(float(enrichment_rate) * 100, 1),
        "outbound_drafts": outbound_drafts,
        "emails_sent": emails_sent,
        "error_rate": round((errors / max(emails_sent + outbound_drafts + errors, 1)) * 100, 1),
        "hmx_reachability_delta": round(float(hmx_delta) * 100, 1),
        "opportunity_synthesis_rate": round((opportunity_rate / total_signals) * 100, 1),
    }


def get_pipeline_flow(session: Session) -> Dict[str, int]:
    return {
        "signals": session.exec(select(func.count(Signal.id))).one(),
        "lead_events": session.exec(select(func.count(LeadEvent.id))).one(),
        "enriched": session.exec(select(func.count(LeadEvent.id)).where(LeadEvent.enrichment_status.in_(["ENRICHED_NO_OUTBOUND", "OUTBOUND_SENT"]))).one(),
        "drafted": session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status.in_(["PENDING", "APPROVED", "SENT"]))).one(),
        "reviewed_sent": session.exec(select(func.count(PendingOutbound.id)).where(PendingOutbound.status.in_(["APPROVED", "SENT"]))).one(),
    }


def get_daily_activity(session: Session, days: int = 7) -> List[Dict[str, Any]]:
    since = datetime.utcnow() - timedelta(days=days)
    rows = session.exec(
        select(func.date(LeadEvent.created_at), func.count(LeadEvent.id))
        .where(LeadEvent.created_at >= since)
        .group_by(func.date(LeadEvent.created_at))
        .order_by(func.date(LeadEvent.created_at))
    ).all()
    return [{"day": str(day), "count": count} for day, count in rows]


def get_recent_system_events(session: Session, limit: int = 15) -> List[Dict[str, Any]]:
    tickets = session.exec(select(SupportTicket).order_by(SupportTicket.updated_at.desc()).limit(limit)).all()
    messages = session.exec(select(Message).where(Message.direction == "OUTBOUND").order_by(Message.created_at.desc()).limit(limit)).all()
    output: List[Dict[str, Any]] = []
    for ticket in tickets:
        output.append({"type": "support", "timestamp": ticket.updated_at, "label": ticket.subject, "status": ticket.status})
    for message in messages:
        output.append({"type": "outbound", "timestamp": message.created_at, "label": message.subject, "status": message.status})
    output.sort(key=lambda row: row["timestamp"] or datetime.min, reverse=True)
    return output[:limit]
