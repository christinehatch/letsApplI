import React from "react";
import { Phase6SidePanel } from "../phase6/Phase6SidePanel";

export function DummyJobPage() {
  const dummyJob = {
    id: "dummy-123",
    title: "Senior Software Engineer, Developer Productivity",
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      {/* Job content area */}
      <main
        style={{
          flex: 1,
          padding: "24px",
          overflowY: "auto",
        }}
      >
        <h1>{dummyJob.title}</h1>

        <p>
          This is a <strong>dummy job page</strong> used only for Phase 6 visual
          validation.
        </p>

        <p>
          The content below simulates a real job listing, but it is static and
          not connected to any live source.
        </p>

        <h2>About the role</h2>
        <p>
          We are looking for engineers to help improve developer tooling,
          workflows, and internal platforms. Responsibilities and requirements
          are intentionally vague in this dummy view.
        </p>

        <h2>Responsibilities</h2>
        <ul>
          <li>Build internal tools</li>
          <li>Improve developer experience</li>
          <li>Collaborate with cross-functional teams</li>
        </ul>

        <h2>Requirements</h2>
        <ul>
          <li>Experience with modern software systems</li>
          <li>Strong communication skills</li>
        </ul>
      </main>

      {/* Phase 6 side panel */}
      <Phase6SidePanel
        jobId={dummyJob.id}
        jobTitle={dummyJob.title}
      />
    </div>
  );
}
