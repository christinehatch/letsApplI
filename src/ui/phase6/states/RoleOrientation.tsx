import React from "react";
import { Phase6State } from "../Phase6State";

interface RoleOrientationProps {
  jobTitle: string;
  onAdvance: (next: Phase6State) => void;
}

/**
 * RoleOrientation
 *
 * Purpose:
 * - Explain what roles with this title are generally like
 * - WITHOUT reading the job listing
 *
 * Guarantees:
 * - No job text has been read
 * - No interpretation of fit
 * - No recommendations
 */
export function RoleOrientation({
  jobTitle,
  onAdvance,
}: RoleOrientationProps) {
  return (
    <div style={{ padding: "16px" }}>
      <h3>What roles like this usually involve (in general)</h3>


      <p>
        This explanation is based only on the role title:
        <strong> {jobTitle}</strong>.
      </p>

      <p>
        I have <strong>not</strong> read this job listing.
      </p>

      <ul>
        <li>Responsibilities and scope can vary widely by company and team.</li>
        <li>Titles often describe a role family, not a specific day-to-day job.</li>
        <li>Details like tools, expectations, and seniority are usually clarified in the posting itself.</li>
      </ul>

      <p>
        If you want, you can ask me to <strong>read the job listing</strong> and
        help explore it more specifically.
      </p>
      <p>
        I won’t read anything unless you explicitly ask me to.
      </p>

      <button
        onClick={() => onAdvance("CONSENT_REQUESTED")}
        style={{ marginTop: "12px" }}
      >
        Read this job listing together
      </button>
    </div>
  );
}
