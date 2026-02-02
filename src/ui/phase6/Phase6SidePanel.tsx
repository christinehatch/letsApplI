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
}: Phase6SidePanelProps) {
  const [state, setState] = useState<Phase6State>("VIEWING");

  function transition(to: Phase6State) {
    assertValidTransition(state, to);
    setState(to);
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
