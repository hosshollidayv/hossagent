# HossAgent Phase 2 – First Real Intelligence Pipeline

Goal:
Replace one mocked account (DoD) with a recommendation generated from live evidence.

Pipeline

SAM.gov
    ↓
USAspending
    ↓
Federal Register
    ↓
Normalize
    ↓
Evidence Objects
    ↓
Score
    ↓
AI Summary
    ↓
UI

Deliverables

[ ] connectors/sam.py
[ ] connectors/usaspending.py
[ ] connectors/federal_register.py
[ ] models/evidence.py
[ ] services/scoring.py
[ ] services/reasoning.py
[ ] services/account_builder.py

Success Criteria

The UI should NOT know anything about DoD.

Instead it should receive something like:

{
  "name":"Department of Defense",
  "score":91,
  "confidence":"High",
  "evidence":[
      {
          "source":"SAM.gov",
          "title":"AI Test & Evaluation Support",
          "date":"2026-06-22"
      },
      {
          "source":"USAspending",
          "award":"$109,500,000",
          "recipient":"..."
      }
  ]
}

No hardcoded agencies.
No hardcoded scores.
No hardcoded summaries.

Everything generated from evidence.
