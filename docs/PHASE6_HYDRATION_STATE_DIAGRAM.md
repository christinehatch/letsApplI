# Phase 6 — Hydration & Exploration State Diagram

This diagram defines the allowed system states and transitions
during Phase 6.

It is authoritative.

```mermaid


stateDiagram-v2
    [*] --> DISCOVERED

    DISCOVERED --> VIEWING : user selects job

    VIEWING --> ORIENTED : request orientation
    ORIENTED --> VIEWING : dismiss orientation

    VIEWING --> CONSENT_REQUESTED : allow system to read
    ORIENTED --> CONSENT_REQUESTED : allow system to read

    CONSENT_REQUESTED --> CONSENT_GRANTED : confirm consent
    CONSENT_REQUESTED --> EXITED : cancel

    VIEWING --> EXITED : close
    ORIENTED --> EXITED : close
