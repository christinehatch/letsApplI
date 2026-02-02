# ROLE_ARCHETYPES_SPEC.md

## Status
**Authoritative — v0**

This document defines the role archetype system used during **pre-hydration job discovery** in letsA(ppl)I.

---

## 1. Purpose

Role archetypes provide **lightweight, pre-hydration orientation** to help users decide whether a job listing is worth exploring further.

They answer a single question:

> *“Before I click, what kind of work is this role generally associated with?”*

Role archetypes exist to reduce confusion from misleading or ambiguous job titles **without reading the job listing** and **without performing interpretation or personalization**.

---

## 2. What Role Archetypes Are Not

Role archetypes are explicitly **not**:

- Job interpretation
- Fit assessment
- Resume alignment
- Recommendations
- Ranking or prioritization
- Company-specific analysis
- Seniority or compensation inference
- Skill extraction
- Preference learning

If any of the above are required, the system must transition to **hydration + explicit user consent** (Phase 5+).

---

## 3. Core Invariants (Non-Negotiable)

The following rules are system invariants:

1. **Title-only input**  
   Archetypes are derived *only* from the job title string.  
   No job descriptions, requirements, or page content may be read.

2. **No hidden interpretation**  
   Assigning an archetype does not constitute “reading” the job.

3. **Deterministic matching**  
   Archetypes are assigned using ordered, deterministic rules.  
   No probabilistic scoring or confidence estimates are allowed.

4. **First-match-wins**  
   Rules are evaluated top-to-bottom.  
   The first matching rule determines the archetype.

5. **Silence over guessing**  
   If no rule matches, the archetype is `UNKNOWN`.  
   The system must not infer or approximate.

6. **Modes of work, not domains**  
   Archetypes describe *how work is done*, not:
   - industry
   - company
   - technology stack
   - ideology
   - subject matter

7. **Pre-hydration only**  
   Archetypes are valid only during discovery and viewing.  
   They must dissolve once the user begins role-specific exploration.

---

## 4. Canonical Archetypes (v0)

The archetype set is intentionally small and stable.

## Canonical Archetypes (v0)

- `SOFTWARE_ENGINEER`
- `SOFTWARE_ENGINEER_EARLY`
- `ML_ENGINEER`
- `AI_ML_RESEARCHER`
- `DATA_SCIENTIST`
- `PRODUCT_MANAGER`
- `PRODUCT_PROGRAM_MANAGER`
- `TECHNICAL_PROGRAM_MANAGER`
- `AI_SOLUTIONS_ARCHITECT`
- `SOLUTIONS_ENGINEER`
- `DEVREL_COMMUNICATOR`
- `ENGINEERING_MANAGER`
- `UX_PRODUCT_DESIGNER`
- `UX_RESEARCHER`
- `ANALYST_COMMENTATOR`
- `SALES_ACCOUNT`
- `UNKNOWN`


Adding a new archetype is a **design decision**, not an implementation detail.

---

## 5. Archetype Definitions

Each archetype provides:
- a **general orientation**
- common **surprises or misconceptions**

These descriptions are intentionally coarse.

### SOFTWARE_ENGINEER
**Generally**
- Hands-on coding and system building
- Owns production software

**Often surprises**
- Scope varies widely by team
- Less autonomy early on than expected

---

### SOFTWARE_ENGINEER_EARLY
**Generally**
- Entry-level or internship engineering role
- Emphasis on learning and mentorship

**Often surprises**
- High interview bar
- Narrow initial scope

---

### ML_ENGINEER
**Generally**
- Applies ML models in production systems
- Mix of engineering and ML tooling

**Often surprises**
- More infrastructure than modeling
- Less research than expected

---

### AI_ML_RESEARCHER
**Generally**
- Focuses on novel methods or models
- Often research- or publication-oriented

**Often surprises**
- Academic expectations
- Slower product impact

---

### DATA_SCIENTIST
**Generally**
- Analyzes data to inform decisions
- Builds metrics, models, or insights

**Often surprises**
- Analytics-heavy roles
- Communication is critical

---

### PRODUCT_MANAGER
**Generally**
- Owns product direction and prioritization
- Works across engineering, design, and stakeholders

**Often surprises**
- Little direct building
- Heavy coordination and communication

---

### PRODUCT_PROGRAM_MANAGER
**Generally**
- Focuses on execution, timelines, and delivery
- Manages cross-team dependencies

**Often surprises**
- Operational rather than strategic
- Less product decision authority

---

### TECHNICAL_PROGRAM_MANAGER
**Generally**
- Coordinates complex technical initiatives
- Requires system-level understanding

**Often surprises**
- Limited coding
- Success is often invisible

---

### AI_SOLUTIONS_ARCHITECT
**Generally**
- Customer-facing technical role
- Translates product capabilities into use cases

**Often surprises**
- Pre-sales or partner focus
- Less hands-on engineering

---

### SOLUTIONS_ENGINEER
**Generally**
- Technical support for sales or customers
- Builds demos or integrations

**Often surprises**
- High communication load
- Fast context switching

---

### DEVREL_COMMUNICATOR
**Generally**
- Educates or supports developers
- Produces technical content or guidance

**Often surprises**
- Public-facing work
- Content creation is core

---

### ENGINEERING_MANAGER
**Generally**
- Leads engineers and teams
- Responsible for delivery and people

**Often surprises**
- Little coding
- Significant emotional labor

---

### UX_PRODUCT_DESIGNER
**Generally**
- Designs user experiences and interfaces
- Works closely with product and engineering

**Often surprises**
- Storytelling and research matter
- Portfolio outweighs resume

---

### UX_RESEARCHER
**Generally**
- Studies user behavior and needs
- Informs product decisions

**Often surprises**
- Slower feedback loops
- Influence varies by org maturity

---

### ANALYST_COMMENTATOR
**Generally**
- Produces analysis, interpretation, or opinion
- Audience-facing communication role

**Often surprises**
- Less original reporting than expected
- Editorial constraints

---

### SALES_ACCOUNT
**Generally**
- Owns customer relationships and revenue
- Performance is quota-driven

**Often surprises**
- High-pressure environment
- Less technical depth than titles imply

---

### UNKNOWN
**Generally**
- The role does not match a known archetype

**System behavior**
> “This title doesn’t match a known archetype yet.  
> You may want to explore the role directly.”

---

## 6. Ordered Matching Rules (v0)

Archetypes are assigned using ordered pattern matching.

- Matching is case-insensitive
- Patterns apply to the **job title only**
- Seniority words (Senior, Staff, Lead, Principal) are ignored

Rules are evaluated **top → bottom**.  
The **first match wins**.

(See implementation file or appendix for full rule list.)

---

## 7. Relationship to System Phases

- **Phase 4.5 (Discovery):**  
  Archetypes are allowed.

- **Viewed (Inspectable Hydration):**  
  Archetypes may be shown as optional orientation.

- **Phase 5+ (Hydration & AI Assistance):**  
  Archetypes must not substitute for job-specific interpretation.

LLMs may later **propose** archetype mappings, but may never assign them silently.

---

## 8. Design Philosophy

Archetypes intentionally trade precision for honesty.

> It is better for the system to say less  
> than to say something confidently wrong.

Restraint is a feature.

