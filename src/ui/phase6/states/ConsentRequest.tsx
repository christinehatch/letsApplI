import React from "react";
import { Phase6State } from "../Phase6State";

interface ConsentRequestProps {
  onAdvance: (next: Phase6State) => void;
}

/**
 * ConsentRequest
 *
 * Purpose:
 * - Ask for explicit permission to read the job listing
 *
 * Guarantees:
 * - No job content has been read yet
 * - No interpretation has occurred
 * - User retains full control
 */
export function ConsentRequest({ onAdvance }: ConsentRequestProps) {
  return (
    <div style={{ padding: "16px", lineHeight: 1.5 }}>
      <h3>Before we continue</h3>

      <p>
        To go further, I would need to <strong>read the job listing</strong>.
      </p>

      <p>
        Reading the listing means I would:
      </p>

      <ul>
        <li>Review the job description text</li>
        <li>Identify responsibilities, requirements, and expectations</li>
        <li>Help summarize or discuss what’s written there</li>
      </ul>

      <p>
        I have <strong>not</strong> read the job yet.
        Nothing will happen unless you explicitly allow it.
      </p>

      <div style={{ marginTop: "16px" }}>
        <button
          onClick={() => onAdvance("CONSENT_GRANTED")}
          style={{ marginRight: "12px" }}
        >
          Yes, read this job listing
        </button>

        <button
          onClick={() => onAdvance("VIEWING")}
        >
          Go back
        </button>
      </div>
    </div>
  );
}
