from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from models import PendingOutbound, LeadEvent


@dataclass
class OutboundActionResult:
    success: bool
    status: str
    message: str
    outbound_id: Optional[int] = None


def approve_pending_outbound(session: Session, outbound_id: int) -> OutboundActionResult:
    outbound = session.exec(select(PendingOutbound).where(PendingOutbound.id == outbound_id)).first()
    if not outbound:
        return OutboundActionResult(False, "not_found", "Outbound not found")
    outbound.status = "SENT"
    outbound.approved_at = outbound.approved_at or datetime.utcnow()
    outbound.sent_at = datetime.utcnow()
    session.add(outbound)
    event = session.exec(select(LeadEvent).where(LeadEvent.id == outbound.lead_event_id)).first() if outbound.lead_event_id else None
    if event:
        event.enrichment_status = "OUTBOUND_SENT"
        event.status = "CONTACTED"
        event.outbound_subject = outbound.subject
        event.outbound_message = outbound.body
        event.last_contact_at = datetime.utcnow()
        session.add(event)
    session.commit()
    return OutboundActionResult(True, "sent", "Outbound approved and marked sent", outbound.id)


def skip_pending_outbound(session: Session, outbound_id: int, reason: str = "Skipped by customer") -> OutboundActionResult:
    outbound = session.exec(select(PendingOutbound).where(PendingOutbound.id == outbound_id)).first()
    if not outbound:
        return OutboundActionResult(False, "not_found", "Outbound not found")
    outbound.status = "SKIPPED"
    outbound.skipped_reason = reason
    session.add(outbound)
    session.commit()
    return OutboundActionResult(True, "skipped", "Outbound skipped", outbound.id)


def update_draft(session: Session, outbound_id: int, subject: str, body: str) -> OutboundActionResult:
    outbound = session.exec(select(PendingOutbound).where(PendingOutbound.id == outbound_id)).first()
    if not outbound:
        return OutboundActionResult(False, "not_found", "Outbound not found")
    outbound.subject = subject
    outbound.body = body
    outbound.status = "PENDING"
    session.add(outbound)
    session.commit()
    return OutboundActionResult(True, "updated", "Outbound draft updated", outbound.id)
