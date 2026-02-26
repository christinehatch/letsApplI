import React from "react";
import { Phase6State } from "./Phase6State";

import { ViewingNotice } from "./states/ViewingNotice";
import { RoleOrientation } from "./states/RoleOrientation";
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
      return <ViewingNotice onAdvance={onAdvance} />;

    case "ORIENTED":
      return (
        <RoleOrientation
          jobTitle={jobTitle}
          onAdvance={onAdvance}
        />
      );

    // -------------------------
    // Hydration Consent
    // -------------------------
    case "CONSENT_REQUESTED_HYDRATION":
      return (
        <ConsentRequest
          title="Allow reading this job listing?"
          description="To proceed, explicit permission is required to read the job listing."
          onConfirm={() => onAdvance("HYDRATING")}
          onCancel={() => onAdvance("VIEWING")}
        />
      );

    // -------------------------
    // Interpretation Consent
    // -------------------------
    case "CONSENT_REQUESTED_INTERPRETATION":
      return (
        <ConsentRequest
          title="Allow structured interpretation?"
          description="This will analyze the already-read job listing and produce a structured breakdown."
          onConfirm={() => onAdvance("INTERPRETING")}
          onCancel={() => onAdvance("HYDRATED")}
        />
      );

    // -------------------------
    // Transitional States
    // -------------------------
    case "HYDRATING":
    case "INTERPRETING":
      return <ConsentAcknowledgement />;

    case "HYDRATED":
      return (
        <div>
          <ConsentAcknowledgement />

          <div style={{ marginTop: "16px" }}>
            <button onClick={onRequestInterpretation}>
              Analyze this role
            </button>
          </div>
        </div>
      );
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