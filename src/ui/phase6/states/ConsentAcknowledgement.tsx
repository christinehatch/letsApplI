import React from "react";

/**
 * ConsentAcknowledgement
 *
 * Purpose:
 * - Confirm that explicit consent has been granted
 * - Mark the boundary between non-reading and reading phases
 *
 * This component performs NO actions.
 * It exists solely to acknowledge user intent.
 */
export function ConsentAcknowledgement() {
  return (
    <div style={{ padding: "16px", lineHeight: 1.5 }}>
      <h3>Consent received</h3>

      <p>
        You’ve given permission for me to read this job listing.
      </p>

      <p>
        From this point forward, I may reference the content of the posting
        when helping you explore it.
      </p>

      <p>
        You are still in control — you can stop or change direction at any time.
      </p>
    </div>
  );
}
