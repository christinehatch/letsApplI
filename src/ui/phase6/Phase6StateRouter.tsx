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
}

/**
 * Phase 6 State Router
 *
 * Responsibilities:
 * - Map Phase6State → UI component
 *
 * Explicitly forbidden:
 * - State mutation
 * - Job interpretation
 * - URL access
 * - Side effects
 */
export function Phase6StateRouter({
  state,
  jobTitle,
  onAdvance,
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

    case "CONSENT_REQUESTED":
      return <ConsentRequest onAdvance={onAdvance} />;

    case "CONSENT_GRANTED":
      return <ConsentAcknowledgement />;

    default:
      return (
        <div>
          Unknown Phase 6 state: <code>{state}</code>
        </div>
      );
  }
}
