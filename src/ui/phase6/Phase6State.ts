// Phase 6 state model — UI-agnostic and content-blind
// This file MUST NOT import job data, DOM APIs, or network logic.

export type Phase6State =
  | "VIEWING"
  | "ORIENTED"
  | "CONSENT_REQUESTED_HYDRATION"
  | "HYDRATING"
  | "HYDRATED"
  | "CONSENT_REQUESTED_INTERPRETATION"
  | "INTERPRETING"
  | "INTERPRETED";

export const ALLOWED_TRANSITIONS: Record<Phase6State, Phase6State[]> = {
  VIEWING: ["ORIENTED", "CONSENT_REQUESTED_HYDRATION"],

  ORIENTED: ["VIEWING", "CONSENT_REQUESTED_HYDRATION"],

  CONSENT_REQUESTED_HYDRATION: ["VIEWING", "HYDRATING"],

  HYDRATING: ["HYDRATED", "VIEWING"],

  HYDRATED: [
    "VIEWING", // revoke hydration
    "CONSENT_REQUESTED_INTERPRETATION",
  ],

  CONSENT_REQUESTED_INTERPRETATION: [
    "HYDRATED",
    "INTERPRETING",
  ],

  INTERPRETING: ["INTERPRETED", "HYDRATED"],

  INTERPRETED: ["HYDRATED", "VIEWING"],
};
// Type-safe transition guard.
// UI code MUST call this before changing state.
export function canTransition(
  from: Phase6State,
  to: Phase6State
): boolean {
  return ALLOWED_TRANSITIONS[from].includes(to);
}

// Runtime assertion to fail fast in development.
// This prevents silent drift during UI wiring.
export function assertValidTransition(
  from: Phase6State,
  to: Phase6State
): void {
  if (!canTransition(from, to)) {
    throw new Error(
      `Invalid Phase 6 transition: ${from} → ${to}`
    );
  }
}
