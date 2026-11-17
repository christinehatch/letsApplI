# Milestone 6 — Personal Profile & Recommendations

**Status:** Plan, agreed direction 2026-11-17. Not started.
**Replaces:** the "No candidate evaluation or job-fit scoring" rule (see §2).
**Touches:** `AGENTS.md`, `docs/APPLYAI_HANDOFF_CONTRACT.md` (v2, §7), the
`career_explorer` repo (§7).

---

## 1. What we're building

Today, letsA(ppl)I only knows what you type into a search box. You have to go
looking.

After Milestone 6, letsA(ppl)I has a **profile** of you, built from things you
choose to give it:

* your resume, LinkedIn profile, personal website and transcripts
* the skills and tools you list
* what you care about and how you like to work, from conversations in
  applyAI (`career_explorer`)

From that profile it:

1. **recommends roles** — Today fills itself every morning, and each role says
   why it showed up;
2. **vets a role when you ask** — on any job page, "How does this line up with
   me?" shows what matches your profile, what the posting asks for that your
   profile doesn't mention, and the evidence for each.

The guiding sentence:

> **letsA(ppl)I shows how a role lines up with what you've told it, and shows
> its working. It never judges you.**

---

## 2. Rule change

`AGENTS.md` previously said: *"No candidate evaluation or job-fit scoring."*
That rule kept letsA(ppl)I from becoming a black-box ranker. Milestone 6 keeps
that intent but allows **explainable, user-owned matching**:

| Before | After |
|---|---|
| No job-fit scoring | Matching is allowed, but every match lists the profile facts and posting text it rests on. No unexplained number, percentage or grade is ever shown. |
| No candidate evaluation | The system never rates the person ("strong candidate", "not qualified", "you should apply"). It describes overlap and gaps between two documents. |
| No background AI | Unchanged. Automatic recommendations use deterministic matching only. AI reads a source or vets a role only when the user presses a button. |
| All analysis user-initiated | Unchanged for AI. Deterministic profile→search matching may run on every discovery check, like search already does. |
| No career advice | Unchanged. No "you should", no "consider pivoting to", no ranking of career paths. |

---

## 3. Principles

1. **You add every source yourself.** Nothing is pulled in automatically, and
   nothing is fetched from a site you didn't name.
2. **You see what was read.** Every fact in the profile shows where it came
   from ("from resume.pdf, page 1"). You can edit or delete any of them.
3. **Proposal before write.** Facts extracted from a source are proposed;
   only the ones you confirm enter the profile. (Same pattern as
   career_explorer memory, `phase5_4_memory_schema.md`.)
4. **Delete means gone.** Removing a source deletes the file, its text and
   every fact that came only from it. Matches that relied on it disappear.
5. **No identity labels.** There is no "personality type". What you care
   about and how you work are stored as your own statements (preference,
   constraint, goal, self-observation), the kinds career_explorer allows,
   never as an inferred trait.
6. **Explain or don't show.** Any recommendation or vetting claim that can't
   point at its evidence is dropped by the validator, not shown with a caveat.
7. **Local and private.** The profile lives in the local SQLite database and
   `state/profile/` (gitignored). The only time profile text leaves the
   machine is an AI step the user pressed, and the UI says so before the
   first one.

---

## 4. Profile sources

| Source | How it's added | What's kept | AI used? |
|---|---|---|---|
| Resume | Upload PDF or DOCX | File + extracted text | Only when you press **Read it** |
| LinkedIn | Save the profile link (never fetched), and optionally upload LinkedIn's **Save to PDF** | Link; file + extracted text | PDF only, when you press **Read it** |
| Personal website | Paste a URL; that page plus up to 5 same-site pages it links to are fetched when you press **Read it**. Or upload a PDF of the site. | Fetched text, fetch date | Only when you press **Read it** |
| Transcripts | Upload PDF | File + extracted text | Only when you press **Read it** |
| Skills & tools | Typed list, editable chips | The list | No |
| Where & how you want to work | Form: locations, remote/hybrid, level, company size, industries to include or avoid | The answers | No |
| What you care about | Selected items sent from applyAI (§7) | Your approved wording, verbatim | No (already approved in applyAI) |

**LinkedIn note:** LinkedIn blocks automated reading of profiles, and scraping
breaks its terms. The supported route is its own "Save to PDF" button on your
profile page. We do not log in to LinkedIn or fetch linkedin.com URLs.

### What "Read it" extracts

The extractor proposes **facts**, each with a kind and a citation:

* `title` — roles held ("Senior Data Engineer, 2022–2025")
* `skill` — skills, tools, languages ("Python", "dbt", "Kubernetes")
* `domain` — fields worked in ("payments", "health tech")
* `education` — degrees, notable courses (from transcripts)
* `location` — places lived or worked
* `achievement` — a specific thing done, quoted

Every proposed fact carries the exact text span it came from. The validator
rejects any fact whose quoted span isn't in the source text (same rule as
Phase 5.2 evidence spans).

---

## 5. Data model (sketch)

```
profile_sources
  id, kind (resume|linkedin|website|transcript), label, file_path | url,
  extracted_text, added_at, read_at, deleted_at

profile_facts
  id, source_id (nullable for typed facts), kind, text, quote,
  status (proposed|confirmed|rejected), created_at, updated_at

profile_preferences
  id, kind (location|work_mode|level|company_size|industry_in|industry_out),
  value, updated_at

profile_reflections            -- from applyAI (§7)
  id, applyai_memory_id, kind (PREFERENCE|CONSTRAINT|GOAL|SELF_OBSERVATION),
  text (verbatim), received_at, deleted_at

role_vettings                  -- §6.5, one per job, replaced on re-run
  job_id, profile_snapshot_hash, vetting_json, created_at
```

Only `confirmed` facts are ever used for matching or vetting.

---

## 6. Steps

Each step ships on its own and is useful on its own.

### 6.1 Profile page and storage

* A **Profile** tab beside Today / Search / Saved Jobs.
* Add or remove each source in §4; type skills; fill in the "where & how"
  form.
* Plain text extraction from PDF and DOCX happens locally, with no AI.
* **Done when:** sources and typed facts persist, deleting removes the file
  and text, and nothing calls an AI service.

### 6.2 Reading your sources

* A **Read it** button per source sends that source's text to the model and
  gets proposed facts back (§4).
* A review screen lists proposals grouped by kind, each showing its quote.
  You confirm, edit or reject each one, or all of them at once.
* A first-use notice says the text is sent to the model's API.
* **Done when:** only confirmed facts appear in the profile, every fact shows
  its source, and the validator drops any fact without a matching quote.

### 6.3 Recommendations (deterministic)

* From confirmed facts and preferences, propose **saved searches**, e.g.
  titles you've held × your locations ("Data Engineer · San Francisco"), or
  domains × level ("Senior · payments"). You pick which to keep.
* Today uses them like any other saved search, so recommendations show up
  every morning with no AI involved.
* Each Today card gets a **why this showed up** line naming the matched
  facts: "Matches: Python, dbt (resume) · San Francisco (your preferences)".
* Roles in industries you said to avoid are left out, and Today says how many
  were hidden and why.
* **Done when:** a new profile with no saved searches gets a filled Today, and
  every card's reason names real confirmed facts.

### 6.4 Sidebar redesign

* Rebuilt around the profile: your profile summary and saved searches at the
  top, then labelled filters. Remove the broken experience dropdown and the
  duplicate "AI roles only" box.
* Mock up first (a search bar across the top vs. a slim labelled sidebar),
  then build the one chosen.
* **Done when:** every control has a visible label and does what it says.

### 6.5 Vetting a role (on request)

* On a job page, after the role is summarized, a **How does this line up with
  me?** button.
* Input: the validated role interpretation (Phase 5.2) + the confirmed
  profile facts and preferences + any applyAI items the user selected.
* Output, three lists, each item citing both a posting quote and a profile
  fact:
  * **Lines up** — "Posting asks for production Python → your resume: 'built
    Python ETL for …'"
  * **The posting asks for, your profile doesn't mention** — stated neutrally
    ("not in your profile"), never "you lack"
  * **Worth asking them** — things the posting leaves unclear (from the
    existing interpretation's open questions)
* A new validator, modeled on the Phase 5.2/5.3 guards, rejects:
  * any item missing either citation
  * scores, percentages, grades, "fit", "qualified", "strong/weak candidate"
  * advice ("you should apply", "consider learning…")
* Stored per job, so reopening the job doesn't re-run the model, the same way
  role summaries are reused. It is re-run only if the profile changed and you
  ask again.
* **Done when:** vetting runs only on the button, every shown item has both
  citations, and banned language never reaches the UI (with tests in the
  style of `tests/phase5_2`).

### 6.6 What you care about, from applyAI

See §7. Last, because it needs changes in both repos and a contract bump.

### Order

6.1 → 6.2 → 6.3 → 6.4 → 6.5 → 6.6. After 6.3 the "it finds jobs for me"
experience works; 6.5 and 6.6 deepen it.

---

## 7. applyAI (`career_explorer`) link — handoff v2

Handoff v1.0 is one-way (letsA(ppl)I → applyAI) and says neither system ever
compares the two. Milestone 6 needs a **return path** for one thing: memory
items the user chooses to share.

Proposed v2 addition (a major version bump under the v1 contract's §10):

* In applyAI's memory ledger, a **Send to letsA(ppl)I profile** action on
  selected items. The user picks the items; nothing is sent by default
  (career_explorer §7 "Memory Interaction Rule").
* Browser-mediated, like v1: the user's browser posts the selected items to
  letsA(ppl)I, which shows a preview and stores them only on accept. No
  server-to-server calls.
* Only `active` items of the four allowed kinds, verbatim text, plus their ids.
  Deleting an item in either app does not delete it in the other; each app's
  copy has its own delete button.
* letsA(ppl)I uses these items in 6.3 (as preferences and constraints) and
  6.5 (only if selected for that vetting).

The v1 sentence "neither system ever compares the two" changes to: *"letsA(ppl)I
may set a role beside what the user chose to share, showing its evidence,
only when asked. applyAI never sees job matches."*

The contract revision is drafted before 6.6 starts and agreed in both repos.

---

## 8. Out of scope

* Writing or rewriting resumes or cover letters
* Applying to jobs or filling in application forms
* Logging in to LinkedIn or any job site
* Personality tests or inferred traits
* Any single "match score" or ranking number shown to the user
* Telling the user which career to pursue

---

## 9. Open questions

1. **Transcripts:** grades are sensitive and rarely matter to postings.
   Extract only courses and degrees, never grades? (Proposed: yes.)
2. **Website:** *Decided:* the saved page plus up to 5 pages it links to on
   the same site, read only on Read it, and listed after reading. Sites that
   can't be read can be uploaded as a PDF instead.
3. **Re-reading:** when a resume is replaced, keep confirmed facts from the
   old version that the new one doesn't mention? (Proposed: ask.)
4. **Which model** for reading and vetting: the same one Phase 5.2 uses today.
