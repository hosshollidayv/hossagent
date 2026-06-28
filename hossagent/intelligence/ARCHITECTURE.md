# HossAgent Intelligence Engine

## Mission

Given a company or agency...

Produce a recommendation backed by evidence.

---

INPUT

Scale AI
OR
Department of Defense

↓

COLLECT

- SAM.gov
- USAspending
- Federal Register

↓

NORMALIZE

EvidenceItem

↓

SCORE

Evidence Quality

Freshness

Buying Motion

Strategic Fit

↓

REASON

OpenAI

↓

OUTPUT

{
    account,
    score,
    confidence,
    evidence[],
    recommendation,
    citations[]
}

---

Rules

Connectors fetch facts.

Scoring computes scores.

LLMs explain.

UI renders.

Never violate those boundaries.
