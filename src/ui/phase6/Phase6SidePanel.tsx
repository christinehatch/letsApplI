import React, { useState } from "react";

import {
  Phase6State,
  assertValidTransition,
} from "./Phase6State";

import { PhaseHeader } from "./PhaseHeader";
import { Phase6StateRouter } from "./Phase6StateRouter";



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
      revocable: boolean;
    };
  }) => void;
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
export function Phase6SidePanel({
  jobId,
  jobTitle,
  onConsentGranted, // Add this
}: Phase6SidePanelProps)  {
  const [state, setState] = useState<Phase6State>("VIEWING");

  function transition(to: Phase6State) {
    assertValidTransition(state, to);
    setState(to);

    // If the state transition is to CONSENT_GRANTED, construct and emit the payload
    if (to === "CONSENT_GRANTED") {
      onConsentGranted({
        job_id: jobId,
        consent: {
          granted: true,
          scope: "read_job_posting",
          granted_at: new Date().toISOString(),
          revocable: true,
        },
      });
    }
  }

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
    </aside>
  );
}
