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
## Current Work

Tasks actively being developed. Limit to 3–5 items.

- Feed usability
- Search Quality
- Done: tokenized search
- Done: seniority filtering
- Done: synonym mapping
- Done: fallback search
- Daily workflow
- New jobs since last visit
- Skip / Save / Open loop
- Session Start summary
- Keyboard triage (S / K / O)


---

## Next Layer

Features planned soon but not currently active.

- Profile page

- Review mode

- Saved Jobs Review Mode
- Flow: discover job -> save job ⭐ -> review saved jobs -> mark as applied / ignored / archived
- Purpose: turn saved jobs into an actionable pipeline instead of a passive bookmark list
- Acceptance criteria:
- A Saved Jobs view exists
- Jobs show saved date
- User can mark a job as applied, ignored, or archived
- Status updates persist in job_user_state

- Signal-driven discovery
- Job understanding
- capability_domains
- project_signals

- Signal exploration UX
- Filter panels
- Domain exploration cards
- Active filter chips

- Discovery expansion
- Ashby adapter
- SmartRecruiters adapter
- BambooHR adapter
- Workday adapter

- Exploration interface
- Interactive job exploration questions

---

## Future System

Long-term capabilities.

- Personal insight layer
- Application tracking
- Resume intelligence

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

- Chat interface
- Career recommendations
- Project suggestions
- Resume rewriting
