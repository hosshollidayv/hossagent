from __future__ import annotations

from typing import Optional, Dict, Any, List

from sqlmodel import Session, select, func

from models import Customer, BusinessProfile, SupportTicket, LeadEvent, PendingOutbound, Thread
from signals_agent import get_todays_opportunities
from subscription_utils import get_customer_plan_status


def get_customer(session: Session, customer_id: int) -> Optional[Customer]:
    return session.exec(select(Customer).where(Customer.id == customer_id)).first()


def get_customer_profile(session: Session, customer_id: int) -> Optional[BusinessProfile]:
    return session.exec(select(BusinessProfile).where(BusinessProfile.customer_id == customer_id)).first()


def get_customer_summary(session: Session, customer_id: int) -> Dict[str, Any]:
    customer = get_customer(session, customer_id)
    if not customer:
        return {}

    plan_status = get_customer_plan_status(customer)
    profile = get_customer_profile(session, customer_id)
    opportunities = get_todays_opportunities(session, company_id=customer_id, limit=8, include_review_mode=True)
    pending = session.exec(
        select(PendingOutbound).where(
            PendingOutbound.customer_id == customer_id,
            PendingOutbound.status == "PENDING"
        ).order_by(PendingOutbound.created_at.desc()).limit(8)
    ).all()
    signals = session.exec(
        select(LeadEvent).where(LeadEvent.company_id == customer_id).order_by(LeadEvent.created_at.desc()).limit(8)
    ).all()
    threads = session.exec(
        select(Thread).where(Thread.customer_id == customer_id).order_by(Thread.updated_at.desc()).limit(5)
    ).all()

    return {
        "customer": customer,
        "plan_status": plan_status,
        "profile": profile,
        "opportunities": opportunities,
        "pending_outbound": pending,
        "signals": signals,
        "threads": threads,
        "opportunities_count": session.exec(
            select(func.count(LeadEvent.id)).where(
                LeadEvent.company_id == customer_id,
                LeadEvent.enrichment_status.in_(["ENRICHED_NO_OUTBOUND", "OUTBOUND_SENT", "SKIPPED"])
            )
        ).one(),
        "pending_count": session.exec(
            select(func.count(PendingOutbound.id)).where(
                PendingOutbound.customer_id == customer_id,
                PendingOutbound.status == "PENDING"
            )
        ).one(),
    }


def list_customers(session: Session) -> List[Dict[str, Any]]:
    customers = session.exec(select(Customer).order_by(Customer.created_at.desc())).all()
    items: List[Dict[str, Any]] = []
    for customer in customers:
        plan_status = get_customer_plan_status(customer)
        opportunities = session.exec(
            select(func.count(LeadEvent.id)).where(LeadEvent.company_id == customer.id)
        ).one()
        pending = session.exec(
            select(func.count(PendingOutbound.id)).where(
                PendingOutbound.customer_id == customer.id,
                PendingOutbound.status == "PENDING"
            )
        ).one()
        items.append({
            "id": customer.id,
            "company": customer.company,
            "contact_name": customer.contact_name,
            "plan": customer.plan,
            "status": customer.subscription_status,
            "outreach_mode": customer.outreach_mode,
            "opportunities_generated": opportunities,
            "pending_outbound": pending,
            "last_activity": customer.last_login_at or customer.created_at,
            "plan_status": plan_status,
        })
    return items


def list_support_tickets(session: Session) -> List[Dict[str, Any]]:
    tickets = session.exec(select(SupportTicket).order_by(SupportTicket.updated_at.desc())).all()
    items: List[Dict[str, Any]] = []
    for ticket in tickets:
        customer = session.exec(select(Customer).where(Customer.id == ticket.customer_id)).first()
        items.append({
            "id": ticket.id,
            "customer": customer.company if customer else "Unknown",
            "subject": ticket.subject,
            "status": ticket.status,
            "updated_at": ticket.updated_at,
            "body": ticket.body,
            "internal_notes": ticket.internal_notes,
        })
    return items
