import React, {
  useState,
  forwardRef,
  useImperativeHandle,
  useCallback,
} from "react";
import { Phase6State, assertValidTransition } from "./Phase6State";
import { PhaseHeader } from "./PhaseHeader";
import { Phase6StateRouter } from "./Phase6StateRouter";

export type Phase6SidePanelHandle = {
  requestHydration: () => void;
  reset: () => void;
  revoke: () => void;


};

type ConsentScope = "hydrate" | "read_job_posting";

export interface Phase6SidePanelProps {
  jobId: string;
  jobTitle: string;
  /**
   * Handoff hook to Phase 5.1.
   * Called only when state transitions to CONSENT_GRANTED.
   */
  onConsentGranted: (payload: {
    job_id: string;
    consent: {
      granted: boolean;
      scope: string;
      granted_at: string;

    };

  }) => void;

  onConsentRevoked: () => void;
}

/**
 * Phase 6 Side Panel
 *
 * Responsibilities:
 * - Own Phase 6 state
 * - Enforce valid state transitions
 * - Render header + state body
 *
 * Explicitly forbidden:
 * - Reading job content
 * - Fetching URLs
 * - Parsing DOM
 * - Interpreting job text
 */
export const Phase6SidePanel = forwardRef<
  Phase6SidePanelHandle,
  Phase6SidePanelProps
>(function Phase6SidePanel({ jobId, jobTitle, onConsentGranted, onConsentRevoked }, ref) {
  const [state, setState] = useState<Phase6State>("VIEWING");

  // ✅ NEW: Phase 6 is now the single place that decides what scope is being requested.
  const [requestedScope, setRequestedScope] = useState<ConsentScope>("read_job_posting");

  const transition = useCallback(
    (to: Phase6State) => {
      assertValidTransition(state, to);
      setState(to);

      // ✅ Emit payload ONLY at the boundary moment.
      if (to === "CONSENT_GRANTED") {
        onConsentGranted({
          job_id: jobId,
          consent: {
            granted: true,
            scope: requestedScope, // ✅ use requested scope, not a hard-coded string
            granted_at: new Date().toISOString(),
          },
        });
      }
    },
    [jobId, onConsentGranted, requestedScope, state]
  );

  // ✅ NEW: App.tsx can only *ask Phase 6* to start a consent flow.
  // It cannot construct payloads or scopes.
  useImperativeHandle(
  ref,
  () => ({
    requestHydration: () => {
      setRequestedScope("hydrate");
      transition("CONSENT_REQUESTED");
    },

    reset: () => {
      setRequestedScope("read_job_posting");
      transition("VIEWING");
    },

    revoke: () => {
      setRequestedScope("read_job_posting");
      setState("VIEWING");
      onConsentRevoked();   // ✅ now valid
    }
  }),
  [transition, onConsentRevoked]
);

  return (
  <aside
    aria-label="letsApplI Phase 6 Side Panel"
    style={{
      width: "360px",
      borderLeft: "1px solid #ddd",
      padding: "16px",
      display: "flex",
      flexDirection: "column",
      boxSizing: "border-box",
    }}
  >
    <PhaseHeader state={state} />

    <div style={{ marginTop: "16px", flex: 1, overflowY: "auto" }}>
      <Phase6StateRouter
        state={state}
        jobTitle={jobTitle}
        onAdvance={transition}
      />
    </div>

    {/* ✅ Revoke button only visible after consent */}
    {state === "CONSENT_GRANTED" && (
      <button
        onClick={() => {
          setRequestedScope("read_job_posting");
          setState("VIEWING");
          onConsentRevoked();
        }}
        style={{
          marginTop: "16px",
          padding: "8px 12px",
          borderRadius: "8px",
          border: "1px solid #ddd",
          background: "#fff",
          cursor: "pointer",
        }}
      >
        Revoke Access
      </button>
    )}
  </aside>
);
});

Phase6SidePanel.displayName = "Phase6SidePanel";
