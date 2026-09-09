"""Synthetic HossTracker story for a cross-organization healthcare authorization."""


PRIOR_AUTHORIZATION_SCENARIO = {
    "productName": "HossTracker",
    "division": "Healthcare Authorization",
    "theme": "tracker",
    "headline": "Why is this authorization stuck?",
    "intro": (
        "Follow one fictional lumbar MRI authorization across a provider and insurer: "
        "HossTracker exposes the missing document, sends a scoped action request, and "
        "leaves the clinical determination with an authorized reviewer."
    ),
    "workspace": "NSHP-PA-260904-731 / Lumbar MRI authorization",
    "workspaceMeta": "SYNTHETIC PRIOR-AUTHORIZATION WORKSPACE",
    "overviewUrl": "/hosstracker",
    "catalogUrl": "/hosstracker/demo",
    "catalogLabel": "Use cases",
    "boundary": (
        "Entirely synthetic demonstration with no PHI. No medical judgment, live record, "
        "document transfer, coverage determination, patient message, or external mutation."
    ),
    "finishLabel": "Attributable authorization record",
    "finishTitle": "One answer for each audience, without merging their private systems.",
    "finishCta": "Request a HossTracker healthcare pilot",
    "steps": [
        {
            "navTitle": "Receive the request",
            "navMeta": "Two items + one correlation",
            "label": "01 · Receive",
            "caption": (
                "The provider and insurer keep separate records. A shared correlation ID "
                "makes them legible as one cross-organization request."
            ),
            "state": "Received",
            "kicker": "Cross-organization intake",
            "title": "Connect the same work without creating one shared database.",
            "description": (
                "On September 4, fictional Harbor Point Orthopedics requests prior "
                "authorization from fictional Northstar Health Plan for Jordan Vega's "
                "lumbar MRI. HossTracker links the provider order and insurer authorization "
                "through one scoped handoff while each organization retains its own item."
            ),
            "sourceTitle": "Correlated work records",
            "sources": [
                {
                    "kind": "PROV",
                    "name": "HPO-ORDER-4821",
                    "meta": "Harbor Point Orthopedics · created Sep 4, 09:06 ET",
                    "status": "Provider-owned",
                },
                {
                    "kind": "PLAN",
                    "name": "NSHP-PA-260904-731",
                    "meta": "Northstar Health Plan · received Sep 4, 09:08 ET",
                    "status": "Insurer-owned",
                },
                {
                    "kind": "HOSS",
                    "name": "HOSS-91C4-72A8-DEMO",
                    "meta": "Scoped correlation · requested decision Sep 10",
                    "status": "Shared",
                },
            ],
            "metrics": [
                {"label": "Local items", "value": "2", "detail": "Separately controlled"},
                {"label": "Shared handoff", "value": "1", "detail": "Narrowly scoped"},
                {"label": "Decision due", "value": "Sep 10", "detail": "17:00 ET"},
            ],
            "records": [
                {"label": "Requested service", "value": "Lumbar MRI without contrast", "status": "Submitted"},
                {"label": "Provider owner", "value": "Malik Chen · Authorization Coordinator", "status": "Owned"},
                {"label": "Insurer owner", "value": "Prior Authorization Intake", "status": "Team-owned"},
            ],
            "recommendationLabel": "System posture",
            "recommendation": "Track the linked records through intake.",
            "recommendationDetail": (
                "HossTracker can show receipt, ownership, due time, and agreed shared state "
                "without exposing either organization's internal workflow."
            ),
            "guardrailLabel": "Privacy boundary",
            "guardrail": "PASS · synthetic identities and minimum shared context",
            "guardrailDetail": (
                "The walkthrough contains no real patient, provider, insurer, PHI, or live authorization data."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Inspect the intake record",
            "toast": "Synthetic authorization linked · no external system changed",
        },
        {
            "navTitle": "Find the blocker",
            "navMeta": "Missing clinical note",
            "label": "02 · Diagnose",
            "caption": (
                "A useful status names the dependency, its owner, its deadline, and the next action."
            ),
            "state": "Action required",
            "kicker": "Explicit blocker",
            "title": "Turn pending into a concrete request for one missing document.",
            "description": (
                "Northstar intake records that the signed August 30 clinical note was not "
                "included. The authorization cannot enter clinical review until Harbor Point "
                "supplies it. HossTracker records the blocker instead of inferring a reason from silence."
            ),
            "sourceTitle": "Intake evidence",
            "sources": [
                {
                    "kind": "CHK",
                    "name": "Submission completeness check",
                    "meta": "Sep 5, 11:24 ET · Northstar intake",
                    "status": "Recorded",
                },
                {
                    "kind": "MISS",
                    "name": "Signed clinical note dated Aug 30",
                    "meta": "Required submission component · synthetic policy",
                    "status": "Missing",
                },
                {
                    "kind": "BLK",
                    "name": "Missing Documentation",
                    "meta": "Created by Nia Foster · Intake Specialist",
                    "status": "Open",
                },
            ],
            "metrics": [
                {"label": "Elapsed", "value": "1d 2h", "detail": "At detection"},
                {"label": "Documents missing", "value": "1", "detail": "Signed note", "tone": "warn"},
                {"label": "Provider response due", "value": "Sep 9", "detail": "12:00 ET", "tone": "warn"},
            ],
            "records": [
                {"label": "Internal status", "value": "Incomplete submission · clinical review not started", "status": "Insurer-only"},
                {"label": "Shared status", "value": "ACTION_REQUIRED · signed clinical note", "status": "Provider-visible"},
                {"label": "Customer status", "value": "Additional information requested from your provider", "status": "Patient-safe"},
            ],
            "recommendationLabel": "Next action",
            "recommendation": "Ask Harbor Point for the signed August 30 clinical note.",
            "recommendationDetail": (
                "Malik Chen owns the provider response; Northstar intake owns validation after it arrives."
            ),
            "guardrailLabel": "Evidence guardrail",
            "guardrail": "PASS · blocker comes from a recorded intake finding",
            "guardrailDetail": (
                "HossTracker does not invent missing documentation or interpret clinical sufficiency."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Prepare the action request",
            "toast": "Recorded blocker explained · nothing sent",
        },
        {
            "navTitle": "Hoss the request",
            "navMeta": "Scoped portal + deadline",
            "label": "03 · Request",
            "caption": (
                "The dependency travels as structured work, not as an untracked email thread."
            ),
            "state": "Awaiting provider",
            "kicker": "HossHandoff",
            "title": "Deliver one bounded ACTION_REQUIRED request to the right owner.",
            "description": (
                "Northstar issues a synthetic ACTION_REQUIRED event to Harbor Point. The "
                "handoff names the exact document, response deadline, return destination, "
                "allowed visibility, and correlation ID. Malik can respond through a scoped portal."
            ),
            "sourceTitle": "Shared handoff envelope",
            "sources": [
                {
                    "kind": "EVT",
                    "name": "ACTION_REQUIRED",
                    "meta": "Sep 5, 11:26 ET · sender Northstar Health Plan",
                    "status": "Attributable",
                },
                {
                    "kind": "PORT",
                    "name": "Harbor Point response portal",
                    "meta": "Upload + question + acknowledge only",
                    "status": "Scoped",
                },
                {
                    "kind": "DUE",
                    "name": "Response due Sep 9, 12:00 ET",
                    "meta": "Owner Malik Chen · reminder Sep 8",
                    "status": "Explicit",
                },
            ],
            "metrics": [
                {"label": "Shared fields", "value": "9", "detail": "Policy-limited"},
                {"label": "Portal permissions", "value": "3", "detail": "Acknowledge · upload · ask"},
                {"label": "Insurer private fields", "value": "0", "detail": "Exposed"},
            ],
            "records": [
                {"label": "Requested action", "value": "Upload signed Aug 30 clinical note", "status": "Explicit"},
                {"label": "Return destination", "value": "NSHP-PA-260904-731 intake", "status": "Bounded"},
                {"label": "Authorization scope", "value": "Handoff HOSS-91C4-72A8-DEMO only", "status": "Narrow"},
            ],
            "recommendationLabel": "Prepared network action",
            "recommendation": "Send the scoped request to Malik Chen.",
            "recommendationDetail": (
                "The handoff carries only the action, deadline, document slot, reference, and safe status context."
            ),
            "guardrailLabel": "Network guardrail",
            "guardrail": "HOLD · authorized sender action required",
            "guardrailDetail": (
                "The demo prepares an envelope but cannot email the provider, create portal access, or transmit a document."
            ),
            "guardrailTone": "hold",
            "actionLabel": "Simulate authorized send",
            "toast": "Synthetic ACTION_REQUIRED recorded · no portal invitation sent",
        },
        {
            "navTitle": "Receive the response",
            "navMeta": "Document + provenance",
            "label": "04 · Respond",
            "caption": (
                "The provider can complete its bounded task without adopting the insurer's system."
            ),
            "state": "Response received",
            "kicker": "External participation",
            "title": "Resolve the dependency through a lightweight scoped portal.",
            "description": (
                "At 10:42 ET on September 8, Malik acknowledges the request and uploads the "
                "fictional signed clinical note from Harbor Point's portal. HossTracker records "
                "RESPONSE and DOCUMENT_AVAILABLE events, then routes the insurer item back to intake validation."
            ),
            "sourceTitle": "Provider response record",
            "sources": [
                {
                    "kind": "ACK",
                    "name": "Request acknowledged",
                    "meta": "Sep 8, 10:39 ET · Malik Chen",
                    "status": "Provider event",
                },
                {
                    "kind": "DOC",
                    "name": "Signed clinical note · DEMO-PDF-830",
                    "meta": "Sep 8, 10:42 ET · synthetic document hash recorded",
                    "status": "Available",
                },
                {
                    "kind": "RESP",
                    "name": "RESPONSE",
                    "meta": "Harbor Point → Northstar · HOSS-91C4-72A8-DEMO",
                    "status": "Received",
                },
            ],
            "metrics": [
                {"label": "Acceptance latency", "value": "2d 23h", "detail": "Synthetic elapsed"},
                {"label": "Requested documents", "value": "1 / 1", "detail": "Received"},
                {"label": "Clinical decisions", "value": "0", "detail": "At this stage"},
            ],
            "records": [
                {"label": "Blocker", "value": "Missing Documentation", "status": "Resolved"},
                {"label": "Next action", "value": "Validate receipt, then assign clinical review", "status": "Northstar-owned"},
                {"label": "Patient status", "value": "Requested information received; review is next", "status": "Patient-safe"},
            ],
            "recommendationLabel": "Routing result",
            "recommendation": "Return the insurer item to intake validation.",
            "recommendationDetail": (
                "Document receipt resolves the recorded dependency; it does not prove coverage criteria or predetermine the outcome."
            ),
            "guardrailLabel": "Clinical boundary",
            "guardrail": "PASS · document receipt is not a determination",
            "guardrailDetail": (
                "HossTracker records provenance and workflow state but does not read the note as medical judgment."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Route to reviewer queue",
            "toast": "Synthetic document received · no clinical determination made",
        },
        {
            "navTitle": "Make the determination",
            "navMeta": "Authorized clinical review",
            "label": "05 · Decide",
            "caption": (
                "Software organizes the record. A credentialed, authorized reviewer owns the consequential decision."
            ),
            "state": "Reviewer decided",
            "kicker": "Clinical authority",
            "title": "Keep coverage judgment with the named clinical reviewer.",
            "description": (
                "Northstar assigns the complete synthetic record to Dr. Maya Patel, its "
                "authorized clinical reviewer. At 14:18 ET on September 8, Dr. Patel records "
                "the fictional approval. HossAgent did not interpret the note or select the outcome."
            ),
            "sourceTitle": "Determination controls",
            "sources": [
                {
                    "kind": "RBAC",
                    "name": "Dr. Maya Patel",
                    "meta": "Northstar authorized clinical reviewer",
                    "status": "Permitted",
                },
                {
                    "kind": "REV",
                    "name": "Clinical review completed",
                    "meta": "Sep 8, 14:18 ET · synthetic review record CR-731",
                    "status": "Attributable",
                },
                {
                    "kind": "DEC",
                    "name": "Approved",
                    "meta": "Fictional demonstration outcome only",
                    "status": "Reviewer-entered",
                },
            ],
            "metrics": [
                {"label": "Complete inputs", "value": "Yes", "detail": "Intake validated"},
                {"label": "Authorized reviewers", "value": "1", "detail": "Named actor"},
                {"label": "Agent decisions", "value": "0", "detail": "Required boundary"},
            ],
            "records": [
                {"label": "Insurer internal status", "value": "Approved by Dr. Patel · CR-731", "status": "Internal"},
                {"label": "Provider shared status", "value": "Authorization approved · scheduling may proceed", "status": "Shared"},
                {"label": "Patient status", "value": "Your plan approved the requested MRI", "status": "Customer-safe"},
            ],
            "recommendationLabel": "Recorded disposition",
            "recommendation": "APPROVED · entered by Dr. Maya Patel.",
            "recommendationDetail": (
                "The system can now prepare audience-specific notifications and close the shared handoff."
            ),
            "guardrailLabel": "Decision guardrail",
            "guardrail": "PASS · authorized reviewer—not the agent—decided",
            "guardrailDetail": (
                "No automation, language model, or workflow rule made or simulated medical judgment."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Prepare status projections",
            "toast": "Synthetic reviewer determination recorded · no live authorization changed",
        },
        {
            "navTitle": "Publish the truth",
            "navMeta": "Three views + one audit chain",
            "label": "06 · Record",
            "caption": (
                "Each audience receives the truth it is authorized to see, tied to the same attributable outcome."
            ),
            "state": "Complete",
            "kicker": "Role-safe operational record",
            "title": "Answer why it was stuck, who resolved it, and what happens next.",
            "description": (
                "The final synthetic record connects the missing-document blocker, scoped "
                "provider response, authorized review, decision time, status projections, and "
                "both local identifiers through one immutable HossHandoff history."
            ),
            "sourceTitle": "Audience-specific projections",
            "sources": [
                {
                    "kind": "PLAN",
                    "name": "Northstar internal record",
                    "meta": "Reviewer, intake events, policy trace, and audit metadata",
                    "status": "Private",
                },
                {
                    "kind": "PROV",
                    "name": "Harbor Point shared record",
                    "meta": "Approved · reference + validity window + next action",
                    "status": "Scoped",
                },
                {
                    "kind": "PAT",
                    "name": "Jordan's status view",
                    "meta": "Approved · provider will contact you about scheduling",
                    "status": "Customer-safe",
                },
            ],
            "metrics": [
                {"label": "End-to-end time", "value": "4d 5h", "detail": "Synthetic timeline"},
                {"label": "External wait", "value": "2d 23h", "detail": "Explicitly measured"},
                {"label": "Audit gaps", "value": "0", "detail": "Every event attributed"},
            ],
            "records": [
                {"label": "Why it was stuck", "value": "Signed Aug 30 clinical note was missing", "status": "Explained"},
                {"label": "Who resolved it", "value": "Malik Chen responded; Dr. Maya Patel decided", "status": "Attributable"},
                {"label": "What happens next", "value": "Harbor Point contacts patient to schedule", "status": "Provider-owned"},
            ],
            "recommendationLabel": "Customer artifact",
            "recommendation": "Attributable authorization record ready.",
            "recommendationDetail": (
                "The provider, insurer, and patient receive appropriate status projections "
                "without sharing one mutable item or exposing private operational detail."
            ),
            "guardrailLabel": "Release boundary",
            "guardrail": "PASS · synthetic artifact only",
            "guardrailDetail": (
                "No PHI, medical judgment, live mutation, document, notification, portal access, or coverage action was created."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Preview authorization record",
            "toast": "Synthetic authorization artifact generated · no file written",
            "artifact": {
                "type": "CROSS-ORGANIZATION AUTHORIZATION RECORD",
                "decision": "APPROVED · FICTIONAL DEMONSTRATION",
                "owner": "Dr. Maya Patel · Authorized Clinical Reviewer",
                "reference": "NSHP-PA-260904-731 · HPO-ORDER-4821 · HOSS-91C4-72A8-DEMO",
            },
        },
    ],
}
