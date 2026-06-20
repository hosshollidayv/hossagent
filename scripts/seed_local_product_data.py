from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import (
    Customer, BusinessProfile, Signal, LeadEvent, PendingOutbound, SupportTicket,
    Company, EnrichmentMetrics, Report, Thread, Message
)


def _customer(company: str, email: str, name: str, niche: str, geography: str, outreach_mode: str = "REVIEW") -> Customer:
    return Customer(
        company=company,
        contact_email=email,
        contact_name=name,
        niche=niche,
        geography=geography,
        outreach_mode=outreach_mode,
        autopilot_enabled=True,
        public_token=f"seed-{company.lower().replace(' ', '-')}",
        plan="paid",
        subscription_status="active",
    )


def main() -> None:
    create_db_and_tables()
    now = datetime.utcnow()
    scenarios = [
        ("Apex Climate Group", "Miami HVAC expansion", "Miami-Dade", "hvac"),
        ("Bayfront Veterinary Care", "new weekend coverage and hiring", "Broward", "veterinary"),
        ("Glow Harbor Med Spa", "second location opening", "Palm Beach", "med spa"),
        ("Sunline Roofing", "storm-related service surge", "Miami-Dade", "roofing"),
        ("Crescent Table Group", "new restaurant in Coral Gables", "Miami-Dade", "restaurant"),
        ("South Florida Route Logistics", "adding last-mile routes", "Broward", "logistics"),
        ("Northshore Family Practice", "new specialty intake program", "Palm Beach", "healthcare"),
    ]

    with Session(engine) as session:
        for idx, (company, signal_text, geography, niche) in enumerate(scenarios, start=1):
            customer = session.exec(select(Customer).where(Customer.company == company)).first()
            if not customer:
                customer = _customer(company, f"hello@{company.lower().replace(' ', '')}.com", "Operations Lead", niche, geography)
                session.add(customer)
                session.flush()

            profile = session.exec(select(BusinessProfile).where(BusinessProfile.customer_id == customer.id)).first()
            if not profile:
                profile = BusinessProfile(
                    customer_id=customer.id,
                    short_description=f"Growth operations for {niche} operators in South Florida.",
                    services="Lead gen, outbound review, signal intelligence",
                    ideal_customer=f"{niche.title()} operators",
                    voice_tone="confident",
                    communication_style="direct",
                    primary_contact_name=customer.contact_name,
                    primary_contact_email=customer.contact_email,
                )
                session.add(profile)

            raw_payload = {
                "url": f"https://news.example.com/{idx}",
                "source_url": f"https://news.example.com/{idx}",
                "headline": signal_text,
                "company": company,
            }
            signal = Signal(
                company_id=customer.id,
                source_type="news",
                raw_payload=json.dumps(raw_payload),
                context_summary=f"{company} was mentioned in a public market update about {signal_text}.",
                geography=geography,
                status="PROMOTED",
                extracted_contact_info=json.dumps({"extracted_emails": [customer.contact_email], "source_confidence": 0.74}),
                created_at=now - timedelta(days=idx),
            )
            session.add(signal)
            session.flush()

            company_row = Company(
                name=company,
                normalized_name=company.lower(),
                domain=f"{company.lower().replace(' ', '')}.com",
                geography=geography,
                source_confidence=0.82,
                source_signal_id=signal.id,
                source_type="news",
                niche=niche,
                enrichment_complete=True,
                last_enriched_at=now - timedelta(days=idx),
            )
            session.add(company_row)
            session.flush()

            event = LeadEvent(
                company_id=customer.id,
                signal_id=signal.id,
                company_table_id=company_row.id,
                lead_company=company,
                lead_domain=f"{company.lower().replace(' ', '')}.com",
                summary=f"{company} is showing a commercial signal: {signal_text}.",
                category="growth_signal",
                urgency_score=78 - idx,
                status="CONTACTED" if idx % 2 == 0 else "NEW",
                recommended_action="Review and send a relevance-based outreach note.",
                outbound_message=f"Hi {company}, we noticed the market signal around {signal_text}.",
                outbound_subject=f"Quick note on {company}",
                enrichment_status="OUTBOUND_SENT" if idx % 2 == 0 else "ENRICHED_NO_OUTBOUND",
                enrichment_attempts=2,
                last_enrichment_at=now - timedelta(hours=idx * 2),
                enriched_email=f"ops@{company.lower().replace(' ', '')}.com",
                enriched_contact_name="Operations Lead",
                enriched_company_name=company,
                domain_confidence=0.88,
                email_confidence=0.81,
                phone_confidence=0.62,
                enriched_at=now - timedelta(hours=idx),
                enrichment_mission_log=json.dumps([
                    {"timestamp": (now - timedelta(days=idx)).isoformat(), "phase": "SignalNet", "action": "Captured source signal"},
                    {"timestamp": (now - timedelta(hours=idx * 2)).isoformat(), "phase": "ARCHANGEL", "action": "Identified contact channel"},
                ]),
            )
            session.add(event)
            session.flush()

            outbound = PendingOutbound(
                customer_id=customer.id,
                lead_event_id=event.id,
                to_email=f"ops@{company.lower().replace(' ', '')}.com",
                to_name="Operations Lead",
                subject=f"{company} and the recent market move",
                body=f"Hi {company}, we noticed your recent market signal around {signal_text}.",
                context_summary=f"Opportunity generated from a public signal in {geography}.",
                status="SENT" if idx % 2 == 0 else "PENDING",
                approved_at=now - timedelta(hours=idx) if idx % 2 == 0 else None,
                sent_at=now - timedelta(minutes=idx * 20) if idx % 2 == 0 else None,
                created_at=now - timedelta(days=idx),
            )
            session.add(outbound)

            report = Report(
                customer_id=customer.id,
                lead_event_id=event.id,
                title=f"Signal brief: {company}",
                description="Local opportunity intelligence note",
                content=f"Observed signal: {signal_text}",
                report_type="opportunity",
            )
            session.add(report)

            thread = Thread(
                customer_id=customer.id,
                lead_event_id=event.id,
                lead_company=company,
                lead_name="Operations Lead",
                lead_email=f"ops@{company.lower().replace(' ', '')}.com",
                status="OPEN",
                last_summary="Awaiting response",
            )
            session.add(thread)
            session.flush()

            session.add(Message(
                thread_id=thread.id,
                lead_event_id=event.id,
                customer_id=customer.id,
                direction="OUTBOUND",
                from_email=customer.contact_email,
                to_email=f"ops@{company.lower().replace(' ', '')}.com",
                subject=f"{company} and the recent market move",
                body_text=f"Hi {company}, we noticed your recent market signal around {signal_text}.",
                status="SENT" if idx % 2 == 0 else "DRAFT",
                generated_by="AI",
            ))

            session.add(SupportTicket(
                customer_id=customer.id,
                subject=f"Question about {company} signal routing",
                body="Customer wants a review of the latest outbound draft.",
                status="open" if idx % 2 else "in_progress",
                internal_notes="Seeded support workflow"
            ))

            session.add(EnrichmentMetrics(
                source_type="news",
                total_leads=1,
                enriched_leads=1,
                enrichment_rate=100.0,
                domains_discovered=1,
                emails_discovered=1,
                phones_discovered=1,
                avg_attempts_per_lead=2.0,
                outbound_sent=1 if idx % 2 == 0 else 0,
                replies_received=0,
                reply_rate=0.0,
                period_start=now - timedelta(days=7),
            ))

        session.commit()
        print("Seeded local product data.")


if __name__ == "__main__":
    main()
