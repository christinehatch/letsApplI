import React, { useState } from "react";
import { Phase6SidePanel } from "../phase6/Phase6SidePanel";

export function App() {
  // --- State ---
  const [selectedJob, setSelectedJob] = useState<any>(null); // State to track the active selection
  const [hydratedContent, setHydratedContent] = useState<string | null>(null);
  const [requirements, setRequirements] = useState<string[]>([]);
  const [view, setView] = useState<'raw' | 'structured'>('raw');
  const [isReading, setIsReading] = useState(false);
  const [availableJobs] = useState([
  {
    id: "stripe:7409686",
    title: "Software Engineer, Product",
    company: "Stripe",
    url: "https://boards.greenhouse.io/stripe/jobs/7409686"
  }
]);

  // --- Handlers ---
  const handleJobSelect = (job: any) => {
    setSelectedJob(job);
    // CRITICAL: Reset hydration when switching jobs to maintain the "Wall"
    setHydratedContent(null);
    setRequirements([]);
    setView('raw');
  };

  const handleConsentHandoff = async (payload: any) => {
    console.log("Phase 6 Handoff Emitted:", payload);
    setIsReading(true);

    try {
      const response = await fetch('http://localhost:8000/api/read-job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.detail || result.error) {
        setHydratedContent(`Error: ${result.detail || result.error}`);
      } else {
        setHydratedContent(result.content);
        // If backend returned interpretation results, populate them
        if (result.requirements && result.requirements.length > 0) {
          setRequirements(result.requirements);
          setView('structured');
          console.log("Phase 5.2 Interpretation received.");
        } else {
          setRequirements([]);
          setView('raw');
          console.log("Phase 5.1 Hydration complete.");
        }
      }
    } catch (error) {
      console.error("CLI Bridge Handoff failed:", error);
      setHydratedContent("Failed to connect to the backend bridge.");
    } finally {
      setIsReading(false);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui, sans-serif" }}>
      {/* 1. Daily Feed (Left Sidebar) */}
      <aside style={{ width: "320px", borderRight: "1px solid #eee", padding: "20px", backgroundColor: "#fff" }}>
        <h2 style={{ fontSize: "18px", marginBottom: "20px" }}>Daily Feed</h2>
        {availableJobs.map(job => (
          <div
            key={job.id}
            onClick={() => handleJobSelect(job)} // Select the job card
            style={{
              padding: "16px",
              border: selectedJob?.id === job.id ? "2px solid #0070f3" : "1px solid #eee",
              borderRadius: "12px",
              marginBottom: "12px",
              cursor: "pointer",
              backgroundColor: selectedJob?.id === job.id ? "#f0f7ff" : "#fff"
            }}
          >
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#0070f3", marginBottom: "#4px" }}>{job.company}</div>
            <div style={{ fontWeight: 600, fontSize: "14px" }}>{job.title}</div>
          </div>
        ))}
      </aside>

      {/* 2. Main Content Area (Center) */}
      <main style={{
        flex: 1,
        padding: "40px", // Standard padding for the Shared Reasoning Space
        backgroundColor: "#fafafa",
        overflowY: "auto",
        display: "flex",
        flexDirection: "column"
      }}>
        {!selectedJob ? (
          <div style={{textAlign: "center", marginTop: "100px", color: "#666"}}>
            <h1>letsA(ppl)I Discovery</h1>
            <p>Select a job from your daily feed to begin exploration.</p>
          </div>
      ) : (
          <>
            {isReading && <p style={{color: "#0070f3"}}><em>System is reading and interpreting...</em></p>}

            {!hydratedContent ? (
  /* The Choice Gate - Structural Honesty */
  <div style={{ textAlign: "center", padding: "60px", backgroundColor: "#fff", borderRadius: "12px", border: "1px solid #eee" }}>
    <h2 style={{ color: "#333" }}>{selectedJob.title} at {selectedJob.company}</h2>
    <p style={{ color: "#666", marginBottom: "32px" }}>How would you like to explore this role?</p>

    <div style={{ display: "flex", gap: "20px", justifyContent: "center" }}>
     <button
         onClick={() => handleConsentHandoff({
           job_id: selectedJob.id,
           request_to_fetch: true,
           consent: {
             scope: "hydrate", // The new, strictly-limited authority level
             granted_at: new Date().toISOString(),
             revocable: true
          }
        })}
          style={{
            padding: "16px 24px",
            borderRadius: "8px",
            backgroundColor: "#0070f3",
            color: "#fff",
            border: "none",
            cursor: "pointer",
            fontWeight: "bold"
          }}
      >
        Explore Together
        <div style={{fontWeight: "normal", fontSize: "12px", marginTop: "4px", opacity: 0.9}}>
          I will fetch a copy of this posting to reason about it with you.
        </div>
      </button>

      <a
          href={selectedJob.url}
          target="_blank"
          rel="noreferrer"
          style={{
            padding: "16px 24px",
            borderRadius: "8px",
            border: "1px solid #ddd",
            color: "#333",
            textDecoration: "none",
            fontWeight: "bold"
          }}
      >
        View on Company Site
        <div style={{fontWeight: "normal", fontSize: "12px", marginTop: "4px", color: "#666"}}>
          Open the live listing in a new tab.
        </div>
      </a>
    </div>
  </div>
            ) : (
                /* Hydrated Analysis View (Phase 5.1 & 5.2) */
<div style={{ marginTop: "24px" }}>
  <div style={{ display: "flex", gap: "10px", marginBottom: "16px" }}>
    <button onClick={() => setView('structured')} style={tabStyle(view === 'structured')}>
      Structured Interpretation (5.2)
    </button>
    <button onClick={() => setView('raw')} style={tabStyle(view === 'raw')}>
      Raw Content (5.1)
    </button>
  </div>

  <div style={contentBoxStyle}>
    {view === 'raw' ? (
      /* PHASE 5.1: The Raw Artifact - Validated by the 'hydrate' scope */
      <pre style={{ whiteSpace: "pre-wrap", fontSize: "14px", color: "#333" }}>
        {hydratedContent}
      </pre>
    ) : (
      /* PHASE 5.2: Interpretation - Gated until 'read_job_posting' authority is granted */
      requirements.length > 0 ? (
        <ul style={{ paddingLeft: "20px" }}>
          {requirements.map((req, i) => (
            <li key={i} style={{ marginBottom: "8px" }}>{req}</li>
          ))}
        </ul>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h3 style={{ color: '#333' }}>Analysis Not Yet Authorized</h3>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            To identify specific requirements and role expectations, you must explicitly allow the system to analyze this posting.
          </p>
          <button
            onClick={() => handleConsentHandoff({
              job_id: selectedJob.id,
              request_to_fetch: false, // This triggers the Phase 5.2 logic path in the bridge
              consent: {
                scope: "read_job_posting", // The higher-authority intelligence key
                granted_at: new Date().toISOString(),
                revocable: true
              }
            })}
            style={{
              padding: "12px 24px",
              backgroundColor: "#0070f3",
              color: "#fff",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            Authorize Analysis (Phase 5.2)
          </button>
        </div>
      )
    )}
  </div>
</div>
            )}
          </>
      )}
      </main>

      {/* 3. Authority SidePanel (Right) */}
      {selectedJob && (
          <Phase6SidePanel
              jobId={selectedJob.id}
              jobTitle={selectedJob.title}
              onConsentGranted={handleConsentHandoff}
          />
      )}
    </div>
  );
}

// Styling Helpers
const tabStyle = (active: boolean) => ({
  padding: "8px 16px", borderRadius: "20px", border: "none",
  backgroundColor: active ? "#0070f3" : "#eee", color: active ? "#fff" : "#333",
  cursor: "pointer", fontWeight: 600
});

const contentBoxStyle = {
  padding: "24px", border: "1px solid #0070f3", borderRadius: "12px",
  backgroundColor: "#fff", boxShadow: "0 4px 12px rgba(0,0,0,0.05)"
};