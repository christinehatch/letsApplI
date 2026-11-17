# letsA(ppl)I Development Kanban

## NORTH STAR

Core product direction and decision anchor.

- A daily job exploration tool that explains roles, reveals patterns in interests,
  and helps the user navigate their career intentionally.

---

## Completed Foundations

Major capabilities already shipped and stable.

- Phase 0–2 System Foundations
- Phase 3 Provider Integrations
- Phase 4 Discovery Engine
- Phase 5.1 Hydration
- Phase 6 Exploration UI (partial)
- AI relevance signal extractor
- Signal-based discovery filtering

---

- Add description to AI relevance scoring
- AI badge in job cards
- AI feed filter
- Add role_summary to interpretation
- Save job button
- Saved jobs page
- Job status transitions
- New jobs since last visit
- Skip / Save / Open loop
- A Saved Jobs view exists
- User can mark a job as applied, ignored, or archived
- Status updates persist in job_user_state
- Done: tokenized search
- Done: seniority filtering
- Done: synonym mapping
- Done: fallback search
- Done: applyAI role handoff (envelope endpoint, Explore in applyAI preview) — contract v1.0 locked
- Done: Analyze Role reuses saved interpretations instead of re-running the LLM
- Done: Today (saved searches, one-at-a-time triage, caught-up)
- Done: Ashby adapter; 55 verified company boards (34 Greenhouse, 21 Ashby)
- Done: roles that leave their board are closed and hidden
- Done: real posted dates; Search and Today list newest first
- Done: Search page leads with the jobs (count, area chips, paged list)
## Current Work

Tasks actively being developed. Limit to 3–5 items.

- Milestone 6 — Personal Profile & Recommendations (plan: docs/PROFILE_PLAN.md)
  - 6.1 Profile page and storage
  - 6.2 Reading your sources (user-triggered, proposed facts)
  - 6.3 Recommendations: profile → saved searches, "why this showed up"
  - 6.4 Sidebar redesign around the profile
  - 6.5 "How does this line up with me?" (user-triggered vetting)
  - 6.6 applyAI return path (handoff contract v2)
- applyAI handoff: confirm "Send to applyAI" opens applyAI in a new tab (regular browser)


---

## Next Layer

Features planned soon but not currently active.

- Search gaps: "or" locations (SF or Remote), South Bay cities, working experience filter
- Saved → applied: saved date, Applied button, "saved but not applied" list
- Follow a company
- Keyboard triage (S / K / O), Session Start summary

- Review mode

- Saved Jobs Review Mode
- Flow: discover job -> save job ⭐ -> review saved jobs -> mark as applied / ignored / archived
- Purpose: turn saved jobs into an actionable pipeline instead of a passive bookmark list
- Acceptance criteria:
- Jobs show saved date

- Signal-driven discovery
- Job understanding
- capability_domains
- project_signals

- Signal exploration UX
- Filter panels
- Domain exploration cards
- Active filter chips

- Discovery expansion
- SmartRecruiters adapter
- BambooHR adapter
- Workday adapter

- Exploration interface
- Interactive job exploration questions

---

- Inbox-like UI
## Future System

Long-term capabilities.

- Personal insight layer
- Application tracking

---

- Bridge server service-layer refactor trigger
- Architecture guardrail.
- If bridge_server.py exceeds ~700 lines OR orchestration logic appears in more than three endpoints, introduce a service layer.
- Target structure:
- services/ job_view_service.py interpretation_service.py discovery_service.py profile_service.py
- bridge_server.py should only contain API routing and request validation. All orchestration logic should move to service modules.
- Acceptance criteria:
- bridge_server only handles HTTP routing
- interpretation logic lives in interpretation_service
- job content resolution lives in job_view_service
- discovery logic lives in discovery_service
## Parking Lot

Ideas not scheduled.

- Chat interface (the conversation lives in applyAI / career_explorer)
- Project suggestions
- Resume rewriting
