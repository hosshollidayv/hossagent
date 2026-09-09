"""Synthetic HossTracker scenario for a cross-organization dental handoff."""


DENTAL_READINESS_SCENARIO = {
    "productName": "HossTracker",
    "division": "Dental Readiness Handoff",
    "theme": "tracker",
    "headline": "Hoss this dental verification.",
    "intro": (
        "Follow one fictional Army Reserve unit as it requests a signed DD Form 2813 "
        "from a fictional civilian dental office, resolves a document defect through a "
        "lightweight portal, and prepares an authorized personnel-workflow update."
    ),
    "workspace": "DENT-26-0442 / SPC Maya Torres / DD Form 2813",
    "workspaceMeta": "FICTIONAL 412TH SUSTAINMENT SUPPORT BATTALION",
    "overviewUrl": "/hosstracker",
    "catalogUrl": "/hosstracker/demo",
    "catalogLabel": "Use cases",
    "boundary": (
        "Entirely synthetic scenario, people, organizations, records, and documents. "
        "No PHI, medical or readiness determination, external contact, document transfer, "
        "or live record mutation."
    ),
    "finishLabel": "Closed-loop handoff",
    "finishTitle": "The unit knows exactly what returned—and what may move next.",
    "finishCta": "Request a HossTracker pilot",
    "steps": [
        {
            "navTitle": "Find the missing form",
            "navMeta": "Item + owner + deadline",
            "label": "01 · Find",
            "caption": (
                "Begin with the exact administrative dependency, not a vague readiness status."
            ),
            "state": "Locating",
            "kicker": "Unit work queue",
            "title": "One personnel action is waiting on one named document.",
            "description": (
                "In this fictional example, SPC Maya Torres's administrative dental-verification "
                "item is owned by readiness clerk SGT Elias Grant at the fictional 412th Sustainment "
                "Support Battalion. The next action is to obtain a provider-signed DD Form 2813 from "
                "fictional Harbor Point Dental by September 11, 2026 at 17:00 ET."
            ),
            "sourceTitle": "Synthetic item record",
            "sources": [
                {
                    "kind": "ITEM",
                    "name": "DENT-26-0442",
                    "meta": "Created Sep 8, 2026 · 09:12 ET",
                    "status": "Waiting",
                },
                {
                    "kind": "DOC",
                    "name": "DD Form 2813 provider verification",
                    "meta": "Provider signature required",
                    "status": "Missing",
                },
                {
                    "kind": "OWN",
                    "name": "SGT Elias Grant",
                    "meta": "Fictional unit readiness clerk",
                    "status": "Accountable",
                },
            ],
            "metrics": [
                {"label": "Due", "value": "Sep 11", "detail": "17:00 ET"},
                {"label": "External actions", "value": "1", "detail": "Signed form"},
                {"label": "Recorded owner", "value": "1", "detail": "SGT Grant"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "Awaiting provider-signed DD Form 2813",
                    "status": "Unit-only",
                },
                {
                    "label": "Shared status",
                    "value": "No handoff sent",
                    "status": "Not started",
                },
                {
                    "label": "Soldier status",
                    "value": "Unit is preparing a request; no action required",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "Explicit next action",
            "recommendation": "Prepare one scoped request to Harbor Point Dental.",
            "recommendationDetail": (
                "Ask only for the signed verification form, name the due time, assign the unit-side "
                "owner, and keep clinical contents outside the operational narrative."
            ),
            "guardrailLabel": "Clinical boundary",
            "guardrail": "PASS · administrative dependency only",
            "guardrailDetail": (
                "HossTracker records that a signed form is needed; it does not determine dental "
                "fitness, assign a dental classification, or interpret clinical information."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Prepare the HossHandoff",
            "toast": "Synthetic work item opened · no military system accessed",
        },
        {
            "navTitle": "Hoss the request",
            "navMeta": "Scope + context + visibility",
            "label": "02 · Handoff",
            "caption": (
                "Package the action, deadline, return path, and disclosure boundary into one "
                "correlated request."
            ),
            "state": "Packaging",
            "kicker": "HossHandoff draft",
            "title": "Send work—not another context-free email.",
            "description": (
                "SGT Grant prepares synthetic handoff HOSS-8D42-B117-2813 for Olivia Chen, the "
                "fictional office manager at Harbor Point Dental. It requests provider review and "
                "signature of DD2813_MTorres_v1_SYNTHETIC.pdf, then return through the scoped portal "
                "by September 11 at 17:00 ET."
            ),
            "sourceTitle": "Prepared handoff envelope",
            "sources": [
                {
                    "kind": "HOSS",
                    "name": "HOSS-8D42-B117-2813",
                    "meta": "412th SSB → Harbor Point Dental",
                    "status": "Draft",
                },
                {
                    "kind": "ACT",
                    "name": "Review, sign, and return one DD Form 2813",
                    "meta": "Requested by SGT Elias Grant",
                    "status": "Scoped",
                },
                {
                    "kind": "FILE",
                    "name": "DD2813_MTorres_v1_SYNTHETIC.pdf",
                    "meta": "Fictional placeholder · portal return only",
                    "status": "Attached",
                },
            ],
            "metrics": [
                {"label": "Due", "value": "3d", "detail": "Sep 11 · 17:00"},
                {"label": "Documents", "value": "1", "detail": "Synthetic PDF"},
                {"label": "Recipients", "value": "1", "detail": "Olivia Chen"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "External verification request prepared",
                    "status": "Unit-only",
                },
                {
                    "label": "Shared status",
                    "value": "REQUESTED · signature and return required",
                    "status": "Counterparty",
                },
                {
                    "label": "Soldier status",
                    "value": "Dental office response requested; no action required",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "Prepared network action",
            "recommendation": "Send a narrowly scoped portal invitation to Olivia Chen.",
            "recommendationDetail": (
                "The envelope exposes only the fictional request context, requested action, due "
                "date, return channel, and correlation ID—not the unit's internal workflow."
            ),
            "guardrailLabel": "Disclosure boundary",
            "guardrail": "HOLD · authorized send required",
            "guardrailDetail": (
                "The walkthrough uses fictional placeholder data. It sends no email, discloses no "
                "PHI, grants no organization-wide access, and transfers no actual document."
            ),
            "guardrailTone": "hold",
            "actionLabel": "Simulate authorized send",
            "toast": "Fictional HossHandoff packaged · nothing transmitted",
        },
        {
            "navTitle": "Office accepts",
            "navMeta": "Portal + ETA + ownership",
            "label": "03 · Accept",
            "caption": (
                "The counterparty can accept and own the work through a lightweight portal without "
                "deploying HossTracker."
            ),
            "state": "Accepted",
            "kicker": "External participant portal",
            "title": "Harbor Point Dental confirms receipt and names the next owner.",
            "description": (
                "At the simulated time of September 8 at 10:06 ET, Olivia Chen opens the fictional "
                "scoped portal, acknowledges the request, accepts it for Harbor Point Dental, and "
                "assigns the document check to fictional provider Dr. Lena Brooks with an estimated "
                "return of September 10 at 15:00 ET."
            ),
            "sourceTitle": "Shared acceptance events",
            "sources": [
                {
                    "kind": "RCV",
                    "name": "Request received",
                    "meta": "Sep 8 · 10:04 ET",
                    "status": "Recorded",
                },
                {
                    "kind": "ACK",
                    "name": "Accepted by Olivia Chen",
                    "meta": "Sep 8 · 10:06 ET",
                    "status": "Accepted",
                },
                {
                    "kind": "ETA",
                    "name": "Estimated return Sep 10",
                    "meta": "15:00 ET · before requested due time",
                    "status": "Provided",
                },
            ],
            "metrics": [
                {"label": "Acceptance", "value": "54m", "detail": "Synthetic latency"},
                {"label": "Recipient owner", "value": "Dr. Brooks", "detail": "Fictional"},
                {"label": "ETA margin", "value": "26h", "detail": "Before due"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "Counterparty accepted; awaiting provider return",
                    "status": "Unit-only",
                },
                {
                    "label": "Shared status",
                    "value": "ACCEPTED · in provider review",
                    "status": "Both parties",
                },
                {
                    "label": "Soldier status",
                    "value": "Dental office expects to respond by Sep 10",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "System response",
            "recommendation": "Wait for the stated ETA; do not generate a follow-up yet.",
            "recommendationDetail": (
                "Receipt, accountable ownership, and an ETA are now explicit, so SGT Grant does not "
                "need to call the office to ask whether the request arrived."
            ),
            "guardrailLabel": "External-access boundary",
            "guardrail": "PASS · access limited to this handoff",
            "guardrailDetail": (
                "The fictional portal participant sees only HOSS-8D42-B117-2813 and cannot access "
                "the unit's item, notes, queue, or other personnel actions."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Review returned document",
            "toast": "Synthetic acceptance recorded · no external party contacted",
        },
        {
            "navTitle": "Fix the signature",
            "navMeta": "Blocker + correction + return",
            "label": "04 · Resolve",
            "caption": (
                "A specific document defect becomes a named, owned blocker instead of an ambiguous "
                "delay."
            ),
            "state": "Resolving",
            "kicker": "Document exception",
            "title": "The first return is missing the provider signature.",
            "description": (
                "The simulated first upload arrives September 9 at 13:48 ET, but the provider "
                "signature field on page 1 is blank. HossTracker records an ACTION_REQUIRED event "
                "without reading clinical fields. Olivia Chen routes the exact defect to Dr. Lena "
                "Brooks, who signs the fictional form and returns a corrected version at 14:32 ET."
            ),
            "sourceTitle": "Blocker and resolution trail",
            "sources": [
                {
                    "kind": "V1",
                    "name": "DD2813_MTorres_v1_SYNTHETIC.pdf",
                    "meta": "Received Sep 9 · 13:48 ET",
                    "status": "Signature blank",
                },
                {
                    "kind": "BLK",
                    "name": "Provider signature required",
                    "meta": "Raised Sep 9 · 13:51 ET",
                    "status": "Action required",
                },
                {
                    "kind": "V2",
                    "name": "DD2813_MTorres_signed_SYNTHETIC.pdf",
                    "meta": "Returned Sep 9 · 14:32 ET",
                    "status": "Corrected",
                },
            ],
            "metrics": [
                {"label": "Blocker age", "value": "41m", "detail": "Recorded to resolved"},
                {"label": "Versions", "value": "2", "detail": "Hash-linked"},
                {"label": "Due margin", "value": "50h", "detail": "Before deadline"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "Corrected return received; clerk review pending",
                    "status": "Unit-only",
                },
                {
                    "label": "Shared status",
                    "value": "DOCUMENT_AVAILABLE · signature issue resolved",
                    "status": "Both parties",
                },
                {
                    "label": "Soldier status",
                    "value": "Dental office corrected the form; no action required",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "Next accountable action",
            "recommendation": "Route the corrected file to SGT Grant for administrative review.",
            "recommendationDetail": (
                "The defect, responder, timestamps, two document versions, and resolution are tied "
                "to one correlation ID, so neither side must reconstruct the exchange from email."
            ),
            "guardrailLabel": "Medical-judgment boundary",
            "guardrail": "PASS · signature presence checked only",
            "guardrailDetail": (
                "The synthetic workflow checks whether a required signature field is populated. It "
                "does not evaluate the signature's clinical assertions or determine readiness."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Send to readiness clerk",
            "toast": "Synthetic blocker resolved · clinical fields not interpreted",
        },
        {
            "navTitle": "Clerk authorizes",
            "navMeta": "Completeness + authority + views",
            "label": "05 · Authorize",
            "caption": (
                "A permitted unit operator—not the automation—decides whether the administrative "
                "workflow may advance."
            ),
            "state": "Reviewing",
            "kicker": "Operator authority",
            "title": "The readiness clerk reviews provenance and administrative completeness.",
            "description": (
                "SGT Elias Grant verifies the fictional correlation ID, expected sender, document "
                "version, return timestamp, and presence of the provider signature. He prepares the "
                "unit item to move from Awaiting External Verification to Verification Received and "
                "prepares the HossHandoff for completion."
            ),
            "sourceTitle": "Synthetic authorization record",
            "sources": [
                {
                    "kind": "RBAC",
                    "name": "SGT Elias Grant",
                    "meta": "Fictional readiness clerk · transition permitted",
                    "status": "Authorized",
                },
                {
                    "kind": "HASH",
                    "name": "demo:8d42…2813",
                    "meta": "Synthetic return-version fingerprint",
                    "status": "Matched",
                },
                {
                    "kind": "AUD",
                    "name": "HA-CHG-DENT-0442",
                    "meta": "Actor + time + visibility projections",
                    "status": "Prepared",
                },
            ],
            "metrics": [
                {"label": "Admin checks", "value": "5 / 5", "detail": "Synthetic"},
                {"label": "Clinical checks", "value": "0", "detail": "Outside scope"},
                {"label": "Live mutations", "value": "0", "detail": "Demo boundary"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "Verification received; personnel advance prepared",
                    "status": "Unit-only",
                },
                {
                    "label": "Shared status",
                    "value": "COMPLETION PREPARED · return accepted",
                    "status": "Counterparty",
                },
                {
                    "label": "Soldier status",
                    "value": "Requested document received; unit review complete",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "Recorded disposition",
            "recommendation": "APPROVE · advance the administrative item to Verification Received.",
            "recommendationDetail": (
                "The clerk approves only the workflow transition and handoff completion. The record "
                "makes no dental classification, deployability, or readiness determination."
            ),
            "guardrailLabel": "Mutation and authority boundary",
            "guardrail": "PASS · fictional clerk action remains unsent",
            "guardrailDetail": (
                "This walkthrough simulates an authorized disposition but cannot update a personnel "
                "system, modify a readiness record, notify the Soldier, or complete a live handoff."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Record synthetic approval",
            "toast": "Administrative transition approved in demo · no live record changed",
        },
        {
            "navTitle": "Close the loop",
            "navMeta": "Outcome + status + audit",
            "label": "06 · Record",
            "caption": (
                "Both organizations retain their own truth while sharing one attributable completion "
                "record."
            ),
            "state": "Complete",
            "kicker": "HossHandoff completion record",
            "title": "The form returns, the dependency closes, and the next owner is explicit.",
            "description": (
                "The synthetic final artifact connects unit item DENT-26-0442, HossHandoff "
                "HOSS-8D42-B117-2813, both document versions, the 41-minute signature correction, "
                "SGT Grant's administrative approval, the three audience-safe statuses, and the next "
                "unit-owned action in one immutable chronology."
            ),
            "sourceTitle": "Closed-loop record contents",
            "sources": [
                {
                    "kind": "ITEM",
                    "name": "DENT-26-0442",
                    "meta": "Verification Received · transition prepared",
                    "status": "Accountable",
                },
                {
                    "kind": "HOSS",
                    "name": "HOSS-8D42-B117-2813",
                    "meta": "Requested → Accepted → Corrected → Completed",
                    "status": "Correlated",
                },
                {
                    "kind": "NEXT",
                    "name": "Unit personnel workflow review",
                    "meta": "Owned by SGT Elias Grant · Sep 10, 09:00 ET",
                    "status": "Explicit",
                },
            ],
            "metrics": [
                {"label": "End-to-end", "value": "29h 20m", "detail": "Synthetic"},
                {"label": "Follow-up calls", "value": "0", "detail": "Shared status"},
                {"label": "Audit gaps", "value": "0", "detail": "Every event attributed"},
            ],
            "records": [
                {
                    "label": "Internal status",
                    "value": "Verification Received · next unit review Sep 10",
                    "status": "Unit-owned",
                },
                {
                    "label": "Shared status",
                    "value": "COMPLETED · signed document returned",
                    "status": "Both parties",
                },
                {
                    "label": "Soldier status",
                    "value": "Requested document received; no action required",
                    "status": "Safe",
                },
            ],
            "recommendationLabel": "Operational outcome",
            "recommendation": "Closed-loop handoff record ready.",
            "recommendationDetail": (
                "The unit can advance its own administrative workflow, the dental office has proof "
                "of completion, and the Soldier sees a useful status without internal notes or "
                "clinical detail."
            ),
            "guardrailLabel": "Final release boundary",
            "guardrail": "PASS · synthetic outcome only",
            "guardrailDetail": (
                "No actual DD Form 2813 exists, no PHI was processed, no external participant was "
                "contacted, and no medical, readiness, or personnel record was created or changed."
            ),
            "guardrailTone": "pass",
            "actionLabel": "Preview completion record",
            "toast": "Synthetic handoff record generated · nothing transmitted or written",
            "artifact": {
                "type": "HOSSHANDOFF COMPLETION RECORD",
                "decision": "ADMINISTRATIVELY COMPLETE / PERSONNEL ADVANCE PREPARED",
                "owner": "SGT Elias Grant · Readiness Clerk (fictional)",
                "reference": "DENT-26-0442 · HOSS-8D42-B117-2813",
            },
        },
    ],
}
