# HossAgent product readiness audit

Date: 2026-08-11

## Release decision

Only public marketing, synthetic product previews, self-guided demos, legal pages, and request-access intake are customer-ready in the current release. Operational workspaces and troubleshooting surfaces are owner-only until their capability, security, data, and integration paths are proven end to end.

## Surface classification

| Surface | Current capability | Readiness | Access |
| --- | --- | --- | --- |
| Marketing landing page | Product positioning and four product paths | Customer-ready | Public |
| Demo hub | Routes to four no-login walkthroughs | Customer-ready | Public |
| Public Sector demo | Synthetic pursuit workflow and artifact preview | Customer-ready as a demo | Public |
| Mission Intelligence overview | Synthetic interactive product preview | Customer-ready as a preview | Public |
| Mission Intelligence demo | Synthetic release-evidence walkthrough | Customer-ready as a demo | Public |
| Private Sector demo | Synthetic account-intelligence walkthrough | Customer-ready as a demo | Public |
| Property Intelligence demo | Synthetic property-intelligence walkthrough | Customer-ready as a demo | Public |
| Request access | Intake for fit review and next steps | Customer-ready | Public |
| Mission Intelligence pilot | Real CSV/JSON validation, cohort analysis, persistence, decision recording, HTML/PDF export | Functional alpha, not customer-ready | Owner-only |
| Public Sector pipeline | Browser-session pipeline repair simulation; no proven live connectors | Not customer-ready | Owner-only |
| Private Sector pipeline | Browser-session pipeline repair simulation; no proven live connectors | Not customer-ready | Owner-only |
| Property Intelligence pipeline | Browser-session pipeline repair simulation; no proven live connectors | Not customer-ready | Owner-only |
| Operator Command | Internal portfolio, readiness, queue, and troubleshooting navigation | Internal operations | Owner-only |
| Legacy customer portal | Real account, outreach, conversation, report, and billing code with unproven production integration and safety posture | Not customer-ready | Owner-only |
| Signup | Creates accounts into the unfinished portal | Disabled for customers | Redirect to request access |

## Evidence behind the decision

- The four demo surfaces are explicitly synthetic, perform no external writes, require no account, and bound their claims in the UI.
- Pipeline repair controls persist only in browser `sessionStorage`; they do not repair live product connectors or data.
- Mission Intelligence has working domain logic and durable records, but the current release does not demonstrate the operational security, deployment, upload governance, and full HTTP integration needed for customer use.
- The legacy portal can trigger outreach, automation, billing, and connector-dependent workflows. Repository code supports dry-run and disabled modes, and production configuration is not proven by the customer release tests.
- Public copy previously linked directly into unfinished workspaces and account creation. Those links are removed in this release.

## Customer release rule

A surface may be labeled available only when its primary job can be completed end to end with real inputs, durable state, appropriate authorization, safe failure behavior, and a tested external-integration path. Until then, customer access is limited to the bounded demo or preview.
