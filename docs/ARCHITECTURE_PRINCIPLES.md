# letsA(ppl)I Architecture Principles

## Human Authority

All meaningful actions must originate from explicit user intent.

## Phase Isolation

System behavior is separated into phases:

1. Discovery
2. Hydration
3. Interpretation
4. Fit Analysis

Each phase consumes artifacts produced by the previous phase.

## Artifact Discipline

LLM reasoning must operate on explicit artifacts, not raw browsing.

## Determinism Where Possible

Interpretation outputs must be validated and deterministic where required.

## No Autonomous Actions

The system must never:

- Apply to jobs
- Send messages
- Submit forms
