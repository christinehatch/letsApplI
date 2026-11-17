# ACTIVE_WORKSTREAM

## Project North Star

"A daily job exploration tool that explains roles
and reveals patterns in the job market."

## Current Work Focus

Primary focus is exploration workflow quality and triage usability.
Current work is UI/interaction-first, not architecture refactoring.

## Current Work items

- Feed usability and orientation
- Keyboard triage stability (`J`, `Shift+J`, `S`, `K`, `O`, `A`)
- Saved pipeline usability (status changes, drag/drop, inbox navigation)
- Search UX reliability (URL state + local draft behavior)
- Search relevance improvements (tokenized matching and safe synonym handling)
- Market alignment as exploration entry point
- Context persistence between market/feed/review states

## Immediate Next Feature

Continue exploration workflow refinement with emphasis on:

- predictable feed context retention
- low-friction triage loops in both feed and saved pipeline
- clear transitions between role discovery and job review

## Recently Completed in This Session

- Reused shared `JobCard` for center discovery grid.
- Restored SavedJobsBoard action wiring:
  - dropdown -> user state update
  - drag/drop -> user state update
  - star toggle -> priority/save action
- Added Saved Jobs pipeline framing header and back navigation.
- Removed distracting drag button; made full card draggable.
- Reduced disorienting drop motion by disabling drop animation.
- Added saved-sidebar local search (`company`/`title`, case-insensitive).
