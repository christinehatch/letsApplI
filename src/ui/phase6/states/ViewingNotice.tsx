import React from "react";
import { Phase6State } from "../Phase6State";

interface ViewingNoticeProps {
  onAdvance: (next: Phase6State) => void;
}

/**
 * ViewingNotice
 *
 * Purpose:
 * - Make it explicit that the system has NOT read the job
 * - Anchor the user in Phase 6 before any interpretation
 *
 * This component must remain:
 * - Declarative
 * - Non-interpretive
 * - Non-reading
 */
export function ViewingNotice({ onAdvance }: ViewingNoticeProps) {
  return (
    <div style={{ padding: "16px" }}>
      <h3>Job posting loaded</h3>

      <p>
        The system has loaded this job listing so you can read it.
      </p>

      <p>
        If you'd like, I can analyze the role to extract requirements and
        capability signals.
      </p>

      <button
        onClick={() => onAdvance("CONSENT_REQUESTED_INTERPRETATION")}
        style={{ marginTop: "12px" }}
      >
        Analyze role
      </button>
    </div>
  );
}
