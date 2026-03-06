import React from "react";
import { Phase6State } from "./Phase6State";


import { ConsentRequest } from "./states/ConsentRequest";
import { ConsentAcknowledgement } from "./states/ConsentAcknowledgement";

interface Phase6StateRouterProps {
  state: Phase6State;
  jobTitle: string;
  onAdvance: (next: Phase6State) => void;
  onRequestInterpretation: () => void;
}

export function Phase6StateRouter({
                                    state,
                                    jobTitle,
                                    onAdvance,
                                    onRequestInterpretation,
}: Phase6StateRouterProps) {
  switch (state) {

  case "VIEWING":
  return (
    <div>
      <p>The job posting has been loaded.</p>

      <p>
        You can explore the raw posting yourself, or ask me to analyze
        the role structure.
      </p>

      <p>I can extract:</p>

      <ul>
        <li>Explicit requirements</li>
        <li>Capability domains</li>
        <li>Signals about the role’s emphasis</li>
      </ul>

      <p style={{ fontSize: "13px", color: "#666" }}>
        This analysis does not evaluate you or recommend actions.
      </p>

      <button onClick={onRequestInterpretation}>
        Analyze Role
      </button>
    </div>
  );

  case "CONSENT_REQUESTED_INTERPRETATION":
    return (
      <ConsentRequest
        title="Analyze this role?"
        description="This will analyze the job posting and extract requirements and capability signals."
        onConfirm={() => onAdvance("INTERPRETING")}
        onCancel={() => onAdvance("VIEWING")}
      />
    );

  case "INTERPRETING":
    return <p>Analyzing role…</p>;

  case "INTERPRETED":
    return <ConsentAcknowledgement />;

  default:
      return (
        <div>
          Unknown Phase 6 state: <code>{state}</code>
        </div>
      );
  }
}