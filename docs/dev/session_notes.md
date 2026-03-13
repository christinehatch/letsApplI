## Feature: Manual Context Augmentation

Purpose
Allow users to augment incomplete job hydration when job sites
return partial content.

Architecture
Frontend:
App.tsx

State added:
- additionalContext
- showContextInput

UI flow:
1. Hydrated job content renders.
2. If content is incomplete, user clicks "Add Missing Details".
3. Textarea allows pasting additional job description text.
4. Combined content is sent to:

POST /api/interpret-manual

Backend:
bridge_server.py

Endpoint:
POST /api/interpret-manual

Input:
raw_content

Behavior:
Runs Phase52Interpreter with user supplied raw text.

Result:
Returns interpretation + span_map identical to standard flow.

UX decision:
The trigger button was moved to the job header
(next to "View on Company Site") to ensure users see it immediately.

Why:
Job pages frequently contain large navigation blocks or
footer content that hides missing data issues.

Notes:
This feature does not modify hydration logic.
It only allows user augmentation.
