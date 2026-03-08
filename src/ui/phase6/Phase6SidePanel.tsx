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
  requestInterpretation: () => void;
  completeInterpretation: () => void;
  restoreInterpreted: (interpretation: unknown) => void;
  reset: () => void;
  revoke: () => void;
};

type ConsentScope = "interpret_job_posting";

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
  const [, setInterpretation] = useState<unknown | null>(null);

  // ✅ NEW: Phase 6 is now the single place that decides what scope is being requested.
  const [requestedScope, setRequestedScope] =
  useState<ConsentScope>("interpret_job_posting");

  const transition = useCallback(
  (to: Phase6State) => {
    setState(prev => {
      assertValidTransition(prev, to);
      return to;
    });

    // Fire consent ONLY when entering INTERPRETING
    if (to === "INTERPRETING") {
      onConsentGranted({
        job_id: jobId,
        consent: {
          granted: true,
          scope: requestedScope,
          granted_at: new Date().toISOString(),
        },
      });
    }
  },
  [jobId, onConsentGranted, requestedScope]
);


  // ✅ NEW: App.tsx can only *ask Phase 6* to start a consent flow.
  // It cannot construct payloads or scopes.
  useImperativeHandle(
  ref,
  () => ({

    requestInterpretation: () => {
      setRequestedScope("interpret_job_posting");
      transition("CONSENT_REQUESTED_INTERPRETATION");
    },


    completeInterpretation: () => {
      setState(prev => {
        if (prev === "INTERPRETING") {
          assertValidTransition(prev, "INTERPRETED");
          return "INTERPRETED";
        }
        return prev;
      });
    },

    restoreInterpreted: (interpretation: unknown) => {
      setInterpretation(interpretation);
      setState("INTERPRETED");
    },

    reset: () => {
      setState("VIEWING");
    },

    revoke: () => {
      setRequestedScope("interpret_job_posting");
      setState("VIEWING");
      onConsentRevoked();
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
        onRequestInterpretation={() => {
          setRequestedScope("interpret_job_posting");
          transition("CONSENT_REQUESTED_INTERPRETATION");
        }}
      />
    </div>

    {/* ✅ Revoke button only visible after consent */}
    {(state === "INTERPRETING" || state === "INTERPRETED") && (
  <button
    onClick={() => {
      // Always revoke through controlled transition
      setRequestedScope("interpret_job_posting");
      transition("VIEWING");
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
