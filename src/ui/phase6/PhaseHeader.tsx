import React from "react";
import { Phase6State } from "./Phase6State";

interface PhaseHeaderProps {
  state: Phase6State;
}

/**
 * Phase 6 Header
 *
 * Responsibilities:
 * - Display current phase and state
 * - Provide transparency without interpretation
 *
 * Explicitly forbidden:
 * - Job content
 * - Analysis
 * - Navigation
 */
export function PhaseHeader({ state }: PhaseHeaderProps) {
  return (
    <header>
      <div style={{ fontWeight: "bold" }}>
        Phase 6 — Hydration & Exploration
      </div>
      <div style={{ fontSize: "0.9em", color: "#666" }}>
        State: {state}
      </div>
    </header>
  );
}
