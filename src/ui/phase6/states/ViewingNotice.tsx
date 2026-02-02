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
      <h3>You are viewing a job listing</h3>

      <p>
        I have <strong>not</strong> read this job posting.
      </p>

      <p>
        I can help explain what roles like this are generally about — without
        looking at this listing — if you want.
      </p>

      <button
        onClick={() => onAdvance("ORIENTED")}
        style={{ marginTop: "12px" }}
      >
        Explain this type of role
      </button>
    </div>
  );
}
