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

const actionButtonStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #e5e7eb",
  backgroundColor: "#f9fafb",
  cursor: "pointer",
  fontWeight: 500
};

const secondaryActionButtonStyle: React.CSSProperties = {
  ...actionButtonStyle,
  backgroundColor: "#fff",
  color: "#555"
};

export interface Phase6SidePanelProps {
  jobId: string;
  jobTitle: string;
  loadingArtifacts?: boolean;
  additionalContext: string;
  setAdditionalContext: (value: string) => void;
  handleReinterpretWithContext: () => void;
  isInterpreting: boolean;
  hydrationIncomplete?: boolean;
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
>(function Phase6SidePanel({
  jobId,
  jobTitle,
  loadingArtifacts = false,
  additionalContext,
  setAdditionalContext,
  handleReinterpretWithContext,
  isInterpreting,
  hydrationIncomplete = false,
  onConsentGranted,
  onConsentRevoked
}, ref) {
  const [state, setState] = useState<Phase6State>("VIEWING");
  const [interpretationResult, setInterpretation] = useState<unknown | null>(null);
  const [contextExpanded, setContextExpanded] = useState(false);
  const hasInterpretation = !!interpretationResult;

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
      setInterpretation({});
    },

    restoreInterpreted: (interpretation: unknown) => {
      setInterpretation(interpretation);
      setState("INTERPRETED");
    },

    reset: () => {
      setState("VIEWING");
      setInterpretation(null);
    },

    revoke: () => {
      setRequestedScope("interpret_job_posting");
      setState("VIEWING");
      setInterpretation(null);
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
        loadingArtifacts={loadingArtifacts}
        actionButtonStyle={actionButtonStyle}
        secondaryActionButtonStyle={secondaryActionButtonStyle}
        onAdvance={transition}
        onRequestInterpretation={() => {
          setRequestedScope("interpret_job_posting");
          transition("CONSENT_REQUESTED_INTERPRETATION");
        }}
      />

      {hydrationIncomplete && (
        <div
          style={{
            marginTop: "16px",
            padding: "10px",
            borderRadius: "8px",
            background: "#fff7e6",
            border: "1px solid #ffd591",
            fontSize: "13px"
          }}
        >
          ⚠ Job content may be incomplete.
          <button
            onClick={() => setContextExpanded(true)}
            style={{
              marginLeft: "6px",
              background: "none",
              border: "none",
              color: "#1677ff",
              cursor: "pointer",
              fontWeight: 600
            }}
          >
            Add missing context
          </button>
        </div>
      )}

      <div style={{ marginTop: "24px" }}>
        <h4 style={{ margin: 0 }}>Improve Job Content</h4>
        <button
          onClick={() => setContextExpanded(!contextExpanded)}
          style={{
            background: "none",
            border: "none",
            padding: 0,
            fontWeight: 600,
            cursor: "pointer",
            color: "#444"
          }}
        >
          {contextExpanded ? "▼ Add missing context" : "▶ Add missing context"}
        </button>

        {contextExpanded && (
          <div style={{ marginTop: "12px" }}>
            <p style={{ color: "#666", fontSize: "13px" }}>
              Some job pages load incomplete descriptions. Paste missing sections from the job page
              before analyzing.
            </p>

            <textarea
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              placeholder="Paste additional job description text..."
              style={{
                width: "100%",
                minHeight: "120px",
                padding: "10px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                fontFamily: "inherit",
              }}
            />

            <button
              onClick={handleReinterpretWithContext}
              disabled={!additionalContext.trim() || isInterpreting}
              style={{
                marginTop: "10px",
                padding: "8px 14px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                background: "#fff",
                fontWeight: 600,
                cursor: additionalContext.trim() && !isInterpreting ? "pointer" : "not-allowed",
                opacity: additionalContext.trim() && !isInterpreting ? 1 : 0.6
              }}
            >
              {hasInterpretation ? "Re-run Analysis" : "Analyze Role"}
            </button>
          </div>
        )}
      </div>
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
    style={{ ...actionButtonStyle, marginTop: "16px" }}
  >
    Revoke Access
  </button>
)}
  </aside>
);
});

Phase6SidePanel.displayName = "Phase6SidePanel";
