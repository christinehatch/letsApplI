# Phase 5.2 — LLM Integration Contract

---

## Purpose

This document defines the contractual boundaries governing LLM usage within Phase 5.2 of letsApplI.

Phase 5.2 performs structured, consent-gated analytical interpretation of hydrated job postings. The LLM is used as a **constrained synthesis engine**.

It is **not**:

- A resume advisor
- A recruiter
- A strategist
- A fit evaluator
- A probabilistic predictor

> The LLM must operate strictly within the Phase 5.2 behavioral envelope.

---

## Authority Boundary

**The LLM receives only:**

| Input | Value |
|---|---|
| `job_id` | Identifier for the posting |
| `raw_content` | The hydrated job text |
| `read_at` | Timestamp of retrieval |

**The LLM has no access to:**

- User resume or profile
- Historical memory
- External APIs
- Company knowledge outside `raw_content`

The LLM operates **statelessly and ephemerally**. It cannot persist state or retrieve additional data.

---

## Consent Scope

LLM invocation for Phase 5.2 requires explicit consent scope:

```
interpret_job_posting
```

If consent is revoked:

- No interpretation may be generated
- No structured output may persist
- No derived artifacts may remain in memory

> Phase 5.2 output is **ephemeral and revocable**.

---

## LLM Behavioral Constraints

**The LLM must:**

- Produce structured JSON only
- Conform exactly to the frozen Phase 5.2 schema
- Remain role-centric
- Ground all claims in `raw_content`
- Preserve modality (`required` vs `preferred` vs `optional`)

**The LLM must never:**

- Use personalization or advice
- Evaluate fit or hiring probability
- Use competitive or comparative framing
- Use resume, portfolio, or application language
- Make strategic suggestions

---

## Prohibited Output Types

The LLM must not generate:

- Second-person language (`you`, `your`)
- Applicant framing (`candidates`, `applicants`)
- Resume suggestions or project instructions
- Application tactics or competitive analysis
- Probability estimates
- External technical explanations
- Industry commentary
- Company background not present in `raw_content`

> If uncertain, the LLM must **omit rather than speculate**.

---

## Permitted Output Scope

The LLM may:

- Extract explicit requirements
- Detect repeated themes and capability emphasis signals
- Identify responsibility clusters and collaboration patterns
- Identify seniority **only if explicitly stated**
- Produce a neutral Role Summary
- Produce Project Opportunity Signals *(descriptive only)*

**Human-role phrasing is permitted** when describing job activities — not applicant evaluation:

```
✅ "Engineers in this role would…"
❌ "You should demonstrate…"
```

---

## System Prompt Requirements

**The system prompt must:**

- Reinforce non-advisory constraints
- Explicitly prohibit candidate evaluation, strategic framing, resume language, and probability forecasting
- Reinforce the grounding requirement
- Instruct JSON-only output
- Instruct omission over speculation

**The system prompt must not:**

- Contain examples that drift into strategy
- Include resume alignment guidance
- Include coaching tone

> The system prompt must be **version-controlled**.

---

## Output Schema Requirements

The LLM must return structured JSON with **exactly** these keys:

```json
{
  "RoleSummary": {},
  "RequirementsAnalysis": {},
  "CapabilityEmphasisSignals": {},
  "ProjectOpportunitySignals": {},
  "InterpretationResult": {},
  "confidence": "",
  "schema_version": ""
}
```

- No additional keys are permitted
- Schema shape must match frozen version exactly
- Any schema drift triggers **validation failure**

---

## Determinism Configuration

| Parameter | Value |
|---|---|
| `temperature` | `0` |
| `top_p` | `1` |
| `frequency_penalty` | `0` |
| `presence_penalty` | `0` |

No sampling. No creative variation. Given identical input, output must produce an **identical structural hash** after normalization.

> Determinism violations constitute **contract violations**.

---

## Grounding Requirement

All thematic or synthesized claims must:

- Reference supporting span IDs
- Correspond to substrings in `raw_content`
- Avoid introducing technical domains not present in the text

Grounding is enforced by the validator. **The LLM must not hallucinate.**

---

## Modality Preservation Rule

| Source Language | Must Be Classified As |
|---|---|
| `"preferred"`, `"nice to have"` | `preferred` — must not be elevated to `required` |
| `"minimum"`, `"must"` | `required` |
| `"optional"` | `optional` |

> Modality misclassification constitutes a **violation**.

---

## Structural Limits

The LLM must respect configurable bounds:

| Limit | Value |
|---|---|
| Maximum capability domains | configurable |
| Maximum thematic description length | configurable |
| Maximum extracted requirements | bounded |

No over-clustering or abstraction expansion allowed.

---

## Error Handling

If LLM output fails validation:

```python
raise Phase52ValidationError("Explicit reason")
```

- Do not retry silently
- Do not repair output
- Do not strip advisory language
- Do not degrade gracefully

> **Failure is safer than drift.**

---

## Shadow Mode Requirement

Before activation, the LLM must run in shadow mode:

- Output must pass the validator
- Structural hashes must be logged
- Drift patterns must be reviewed

**Recommended minimum shadow dataset:** 100 postings.

Unlock only after shadow validation passes stability criteria.

---

## Logging Boundaries

**Log on each invocation:**

| Field | |
|---|---|
| `job_id` | `model_version` |
| `schema_version` | `validator_version` |
| Structural hash | Validation result |
| Timestamp | |

**Never log:**

- User resume or personal data
- Sensitive user materials

> Interpretation must remain **isolated from user context**.

---

## Versioning & Change Control

The LLM contract must track:

```
model_name        model_version     prompt_version
schema_version    validator_version contract_version
```

Any change to the behavior spec, schema, validator, model version, or system prompt requires:

1. Contract version increment
2. Entry in `ARCHITECTURE_LOCK.md`

---

## Security Model

Assume LLM output may attempt:

- Advisory drift
- Strategic leakage
- Competitive framing
- Schema injection
- Actor substitution
- Hallucinated or externally-sourced content

> The **validator is the enforcement boundary**. The LLM is an **untrusted generator**.

---

## Phase Separation Guarantee

Phase 5.2 must **never**:

- Evaluate candidate alignment
- Score a resume
- Recommend project creation
- Suggest strategy
- Forecast hiring outcome

Those authorities belong **exclusively to Phase 5.3** under separate consent.

Schema + Validator + Contract together enforce separation.

---

## Contract Violation Definition

A violation occurs if LLM output:

- Breaks schema
- Violates the actor model
- Uses advisory, competitive, or probabilistic language
- Introduces ungrounded claims
- Misclassifies modality
- Produces non-deterministic structure

> Violations must be **logged and rejected**.

---

## Unlock Criteria

Phase 5.2 may be activated **only if**:

- [ ] Behavior spec frozen
- [ ] Schema frozen
- [ ] Validator implemented
- [ ] Determinism verified
- [ ] Shadow mode completed
- [ ] Drift logs reviewed
- [ ] Consent scope expanded intentionally

---

## Contract Philosophy

Phase 5.2 is a **structured analytical interpreter**.

It is not a coach, a strategist, a predictor, or a resume optimizer.

> The LLM exists to synthesize role structure — **nothing more**.

---

*End of Document*
