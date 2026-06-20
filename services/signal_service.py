from __future__ import annotations

from typing import Dict, Any, List, Optional

from sqlmodel import Session, select, func

from models import Signal, LeadEvent, EnrichmentMetrics


def list_recent_signals(session: Session, limit: int = 20, customer_id: Optional[int] = None) -> List[Signal]:
    query = select(Signal).order_by(Signal.created_at.desc()).limit(limit)
    if customer_id:
        query = query.where(Signal.company_id == customer_id)
    return session.exec(query).all()


def get_signal_summary(session: Session) -> Dict[str, Any]:
    total_signals = session.exec(select(func.count(Signal.id))).one()
    total_events = session.exec(select(func.count(LeadEvent.id))).one()
    enriched = session.exec(
        select(func.count(LeadEvent.id)).where(LeadEvent.enrichment_status.in_(["ENRICHED_NO_OUTBOUND", "OUTBOUND_SENT"]))
    ).one()
    return {
        "signals_total": total_signals,
        "lead_events_total": total_events,
        "enrichment_rate": round((enriched / total_events * 100), 1) if total_events else 0.0,
        "by_source": session.exec(select(Signal.source_type, func.count(Signal.id)).group_by(Signal.source_type)).all(),
    }


def list_enrichment_metrics(session: Session) -> List[EnrichmentMetrics]:
    return session.exec(select(EnrichmentMetrics).order_by(EnrichmentMetrics.period_start.desc())).all()
