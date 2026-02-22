# Phase 5.2 — Structured Analytical Output Validator

---

## Purpose

This document defines the validation layer for Phase 5.2.

Phase 5.2 produces structured analytical interpretation of hydrated job content using an LLM. LLM output is **untrusted**.

The validator is responsible for:

- Enforcing schema conformity
- Preventing advisory drift
- Preventing personalization
- Preventing fit evaluation leakage
- Preventing competitive framing
- Enforcing grounding
- Enforcing modality preservation
- Enforcing determinism constraints

> **Validation must reject, not repair.**

---

## Architectural Position

Validation sits between:

```
LLM → Validator → Phase52Interpreter return value
```

If validation fails:

- Raise explicit error
- Do not fallback silently
- Do not auto-correct
- Do not partially accept

**Phase 5.2 must fail closed.**

---

## Validation Layers

Validation is multi-stage.

---

### 1️⃣ Schema Validation

**Goals**

- Enforce exact JSON structure
- Reject unknown fields
- Reject missing required fields
- Reject type mismatches
- Reject null values where disallowed

**Required Checks**

- Top-level keys must match schema exactly
- No extra keys allowed
- No free-form narrative fields
- Arrays must contain expected object shapes
- Strings must not be empty

**Determinism Enforcement**

- Canonical key ordering
- Stable ordering of arrays (sorted by `source_span_start`)
- Whitespace normalization
- Stable numeric formatting

> If normalized output hash changes between identical inputs → **error**.
Schema must include a version identifier that matches the frozen Phase 5.2 schema version.

---

### 2️⃣ Actor & Personalization Filter

Phase 5.2 must never shift from role-centric framing to candidate-centric framing.

**Reject if any field contains:**

| Term | Term |
|---|---|
| `you` | `your` |
| `candidate` | `applicant` |
| `engineer applying` | `someone applying` |
| `best suited` | `good fit` |
| `strong fit` | `ideal` |

**Example Regex**

```python
r"\byou\b"
r"\byour\b"
r"\bcandidate[s]?\b"
r"\bapplicant[s]?\b"
```

**Actor must remain:**

- `"the role"`
- `"the posting"`
- `"the responsibilities"`
- `"the requirements"`

Anything else → **reject**.

---

### 3️⃣ Advisory Verb Filter

Reject if output includes verbs applied to hypothetical actors.

**Disallowed verbs** *(non-exhaustive)*

`should` · `must`* · `need to` · `consider` · `highlight` · `tailor` · `position` · `prepare` · `demonstrate`† · `showcase` · `emphasize`† · `strengthen`

<sup>* Unless directly quoted from `raw_content`</sup>
<sup>† When applied to a candidate</sup>

**Allowed vs. Disallowed**

| ✅ Allowed | ❌ Disallowed |
|---|---|
| `"The posting emphasizes X."` | `"Applicants should emphasize..."` |
| `"The responsibilities demonstrate X."` | `"You should highlight..."` |

> Validator should check subject + verb context where possible.


Actor Framing Enforcement

Phase 5.2 may use human-role language when describing job responsibilities.

Allowed examples:

- “Engineers in this role would design distributed systems.”

- “The individual in this position would collaborate across teams.”

- “Team members are responsible for maintaining production systems.”

- These constructions are permitted only when describing role activities.

However, reject output if human actors are used to:

- Evaluate candidate strength

- Suggest candidate action

- Frame application strategy

- Imply fit or suitability

Reject if output contains:

- “Applicants should…”

- “Candidates would need to…”

- “A strong engineer would…”

- “Someone with experience in X would be ideal…”

Human-role language must remain descriptive, not evaluative.

If actor framing shifts toward applicant evaluation → raise ACTOR_MODEL_VIOLATION.

---

### 4️⃣ Competitive / Outcome Language Filter

Phase 5.2 **cannot forecast**. Reject if output includes:

`competitive` · `likely` · `unlikely` · `high chance` · `strong chance` · `probability` · `odds` · `hiring likelihood` · `market competitiveness`

---

### 5️⃣ Fit Evaluation Filter

No evaluative language allowed. Reject if output includes:

`qualified` · `overqualified` · `underqualified` · `alignment score` · `suitability` · `strong candidate` · `weak candidate`

---

### 6️⃣ Grounding Enforcement

Every thematic or synthesized claim must reference supporting spans.

**Required Structure**

```json
{
  "domain_label": "...",
  "description": "...",
  "evidence_span_ids": ["..."]
}
```

**Validator must:**

- Ensure span IDs exist
- Ensure span ranges are within `raw_content` bounds
- Ensure extracted text matches `raw_content` substring
- Ensure each thematic claim references at least one span

> If no evidence → **reject**. No free-floating themes allowed.

**Lexical Overlap Threshold**

To prevent abstraction drift, validator must enforce a lexical grounding threshold.

For each synthesized thematic description:

- Extract non-stopword tokens

- Compute overlap ratio with tokens present in raw_content

If more than 40% of meaningful tokens do not appear in raw_content, flag as potential grounding violation.

If ratio exceeds configured threshold → raise GROUNDING_VIOLATION.

---

### 7️⃣ Modality Preservation Check

If a requirement is classified as `required`, `preferred`, or `optional`, the validator must verify that `raw_content` contains corresponding modality indicators.

**Source language indicators:**

| Modality | Indicator Words |
|---|---|
| Required | `required`, `must`, `minimum` |
| Preferred | `preferred`, `plus`, `nice to have` |
| Optional | `optional` |

**Example Violation**

```
Source:  "Experience with Kubernetes preferred."
LLM:     "modality": "required"
```

→ **reject**

---

### 8️⃣ Abstraction Boundary Check

Phase 5.2 may synthesize, but **not generalize beyond the text**.

**Validator must reject:**

- External definitions
- Technical explanations not present in source
- Added glossary text
- Expansion beyond wording scope

**Heuristic:** Ensure synthesized descriptions substantially overlap vocabulary in `raw_content`. If excessive new terminology appears → **reject**.

---

### 9️⃣ Seniority Inference Constraint

| ✅ Allowed | ❌ Disallowed |
|---|---|
| Explicit detection of `"Senior"`, `"Staff"`, `"Principal"` | Inferring seniority if not explicitly stated |

**Reject if output includes** (without a direct source span):

- `"senior-level role"`
- `"mid-level position"`
- `"entry-level role"`

---

### 🔟 Structural Limits

To prevent clustering drift, enforce configurable bounds:

| Limit | Value |
|---|---|
| Maximum capability domains | 3–7 (configurable) |
| Maximum thematic description length | configurable |
| Maximum extracted requirement count | bounded |

This prevents runaway abstraction.

---

## Validation Flow

```python
def validate_phase52_output(output_json, raw_content):

    validate_schema(output_json)
    enforce_deterministic_order(output_json)
    reject_if_actor_shift(output_json)
    reject_if_advisory_language(output_json)
    reject_if_fit_language(output_json)
    reject_if_competitive_language(output_json)
    validate_modality_against_source(output_json, raw_content)
    validate_grounding_spans(output_json, raw_content)
    enforce_structural_limits(output_json)

    return output_json  # only if all checks pass
```

If any step fails:

```python
raise Phase52ValidationError("Explicit reason")
```

**No fallback.**

---

## Failure Philosophy

> Phase 5.2 must prefer **failing explicitly** over **drifting subtly**.

Interpretation is safer when strict.
Interpretation must never degrade gracefully.

If validator detects violation:

- No partial JSON return

- No filtered version return

- No advisory stripping

- No silent correction

Phase 5.2 must fail closed to preserve architectural integrity.

---

## Relationship to Phase 5.3

The validator ensures Phase 5.2 **cannot**:

- Perform alignment reasoning
- Infer candidate fit
- Suggest strategic positioning

That authority belongs **exclusively to Phase 5.3** under separate consent. Schema design and the validator enforce phase separation.

---

## Determinism Enforcement (Required)

Phase 5.2 output must be deterministically stable.

Validator must:

- Canonicalize JSON (sorted keys)

- Canonicalize arrays (sorted by source_span_start)

- Normalize whitespace

- Normalize numeric formatting

After normalization:

- Compute structural hash (e.g., SHA256)

- Log hash with job_id and model version

Requirement:

Given identical raw_content, structural hash must be identical.

If hash differs across identical inputs → raise DETERMINISM_VIOLATION.

Determinism enforcement is mandatory, not optional.

---

## Red-Team Testing Plan *(Future)*

Add adversarial tests for:

- Prompt injection inside job text
- Embedded `"You should…"` inside source
- Misleading modality phrasing
- Competitive language inside job text
- Advisory tone embedded in posting

**Validator must:**

- ✅ Allow quoted source language
- ❌ Reject generated advisory language

Advisory or second-person language must only appear inside span-referenced quoted text.

---

##Drift Logging Channel

On validation failure, system must log:

- Violation type

- Offending output fragment

- Associated raw_content excerpt (if relevant)

- Structural hash (if computed)

- Model version

- Timestamp

Logs must not:

- Attempt auto-repair

- Modify output

- Retry silently

Logs exist solely for:

- Drift analysis

- Red-team evaluation

- Model behavior auditing

- Architectural lock review

Drift logging supports enforceability and audit trail integrity.

---

## Architectural Guarantee

If the validator is implemented correctly, Phase 5.2 becomes:

> **A constrained analytical synthesis engine** — not a resume advisor, not a recruiter, not a coach.

This preserves product vision and architectural integrity.

---

*End of Document*
