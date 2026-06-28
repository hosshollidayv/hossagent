# HossAgent Current State

## Working state

HossAgent main dashboard is working.

Current app:
- FastAPI / uvicorn
- Main file: hoss_core.py
- Start command:
  python3 -m uvicorn hoss_core:app --host 0.0.0.0 --port 8000

## Customer dashboard

Current customer-facing dashboard shows:
- Opportunity Intelligence
- Public Sector / Scale AI market lens
- Account Signals
- Active Sources
- Top Score
- Status
- Scan Summary
- Recommended Accounts
- Data Sources
- Account Detail
- Opportunity Profile
- Evidence Trace
- Recommended Action

Removed:
- Saved Views
- Federal AI Evaluation / DoD Modernization / Civilian Agencies / Risk Watch buttons
- Noir/cockpit copy
- AI synthesis caveat
- buyer-propensity wording

## Current live source

Active customer source:
- USAspending

The scan fetches up to 700 records, applies 24-month relevance filtering, and groups account-level signals.

## T&E stack

T&E enrichment is active.

Current categories:
- Evaluation
- Monitoring
- Red Teaming
- Evidence / Reporting
- Agent Harness

Returned accounts now show T&E fit in account summaries and recommended actions.

## Eval console

Internal evaluation console exists at:
/eval

It checks:
- source health
- scan execution
- response shape
- evidence trace population
- recommended action population

## Next logical move

Do not rewrite UI.

Next best move:
- Fix the Active Sources KPI to show just active count cleanly if needed
- Then wire Federal Register as a second source
- Then update eval console to test both USAspending and Federal Register separately
