# Day 1 Walkthrough — letsA(ppl)I

This document describes the **intended Day 1 user experience** for letsA(ppl)I.

It is written from the user’s point of view and reflects the system’s **actual guarantees**, not aspirational behavior.

No phase beyond what is explicitly invoked may run.

---

## 1. Starting the Day

The user begins a daily session by running:

```bash
python run_daily.py
```

The system responds with a prompt:

```
What kind of role are you exploring today?
(e.g. "iOS engineer", "prompt engineer", "AI product")
```

The user enters a short, natural description, for example:

```
iOS engineer
```

This input expresses **intent only**.
It does not grant permission to read, interpret, or analyze any job content.

---

## 2. Daily Discovery Output

The system responds:

```
Generating today’s discovery output…
```

The system performs **discovery only**.

It may:

* Query approved job sources
* Identify relevant job postings
* Collect job identifiers, titles, companies, and links

It must not:

* Read job descriptions
* Interpret job requirements
* Rank or score jobs
* Make recommendations

The system writes a file:

```
DAILY_OUTPUT.md
```

---

## 3. Reviewing the Output

The user opens `DAILY_OUTPUT.md`.

Each job entry includes:

* Job title
* Company
* Link to the posting
* A status indicator (e.g. `unread`)

At this point:

* The system has **not read** any job posting
* The system has **no knowledge** of job content
* No consent has been granted

The user scrolls, reviews, and may click links in their browser.

All browsing occurs **outside the system**.

---

## 4. Choosing to Read a Job

If the user wants the system to read a specific job posting, they explicitly invoke:

```bash
python read_job.py <job_id>
```

Example:

```bash
python read_job.py job-123
```

The system responds with a clear consent boundary:

```
This action will read the job posting.
No interpretation or analysis will occur.
Proceed? (y/n)
```

If the user answers `n`, nothing happens.

If the user answers `y`, **Phase 5.1 (Consent-Scoped Reading)** may run.

---

## 5. Phase 5.1 — Reading Only

When consent is granted:

* The system reads the job posting
* The system displays or stores the raw content
* The system records provenance (job_id, timestamp)

The system explicitly does **not**:

* Interpret meaning
* Extract requirements
* Judge relevance
* Suggest actions

The system must be able to state:

> “I have read this job posting.
> I have not analyzed or interpreted it.”

---

## 6. End of Day 1 Scope

At the end of this walkthrough:

* No interpretation has occurred
* No fit analysis has occurred
* No recommendations have been made
* No downstream phases have been unlocked

The user may stop, reflect, or return later.

Future phases (interpretation, fit analysis, resume refinement) require **separate, explicit consent** and are **not part of Day 1**.

---

## 7. Design Intent

This walkthrough exists to ensure:

* Users understand what the system is doing at every step
* Consent boundaries are visible and meaningful
* The system never appears more intelligent than it is
* Exploration feels safe, calm, and reversible

This document is a **design contract**, not a suggestion.

Any implementation that deviates from this flow must update this walkthrough first.

