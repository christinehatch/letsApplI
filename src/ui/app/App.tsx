import React, { useState, useRef, useEffect } from "react";
import { Phase6SidePanel, type Phase6SidePanelHandle } from "../phase6/Phase6SidePanel";
export function App() {
  // --- State ---
  const [selectedJob, setSelectedJob] = useState<any>(null); // State to track the active selection
  const [hydratedContent, setHydratedContent] = useState<string | null>(null);
  type Requirement = {
  requirement_text: string;
  modality: string;
  source_span_id: string;
};

const [requirements, setRequirements] = useState<Requirement[]>([]);
const [view, setView] = useState<'raw' | 'structured'>('raw')
    const [isReading, setIsReading] = useState(false);
const [availableJobs, setAvailableJobs] = useState<any[]>([]);
const phase6Ref = useRef<Phase6SidePanelHandle | null>(null);
const [userPreviewUrl, setUserPreviewUrl] = useState<string | null>(null);
const [previewVersion, setPreviewVersion] = useState(0);

useEffect(() => {
  const fetchJobs = async () => {
    try {
      const res = await fetch(
        "http://localhost:8000/api/discovery-feed?location=all"
      );

      const data = await res.json();

      setAvailableJobs(
        data.jobs.map((j: any) => ({
          id: j.job_id,
          title: j.title,
          company: j.company,
          url: j.url,
        }))
      );
    } catch (err) {
      console.error("Failed to load discovery feed:", err);
    }
  };

  fetchJobs();
}, []);

  // --- Handlers ---
 const handleJobSelect = (job: any) => {
  setSelectedJob(job);
  setHydratedContent(null);
  setRequirements([]);
  setView("raw");
  setUserPreviewUrl(null);
};

useEffect(() => {
  if (!selectedJob) return;

  const run = async () => {
    // wait one microtask to ensure mount
    await Promise.resolve();

    if (!phase6Ref.current) return;

    phase6Ref.current.reset();

    const hydratePayload = {
      job_id: selectedJob.id,
      consent: {
        granted: true,
        scope: "hydrate",
        granted_at: new Date().toISOString(),
      },
    };

    await handleHydration(hydratePayload);
  };

  run();

}, [selectedJob]);

  const handleConsentRevoked = async () => {
  setRequirements([]);
  setView("raw");

  if (!selectedJob) return;

  const hydratePayload = {
    job_id: selectedJob.id,
    consent: {
      granted: true,
      scope: "hydrate",
      granted_at: new Date().toISOString(),
    },
  };

  await handleHydration(hydratePayload);
};
 const handleConsentHandoff = async (payload: any) => {
  console.log("Phase 6 Handoff Emitted:", payload);

  const scope = payload?.consent?.scope;

  if (!scope) return;


  if (scope === "interpret_job_posting") {
    await handleInterpretation(payload);
  }
};

 const handleHydration = async (payload: any) => {
  setIsReading(true);
  try {
    const response = await fetch(
      "http://localhost:8000/api/hydrate-job",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );

    const result = await response.json();


    if (result.detail || result.error) {
      setHydratedContent(`Error: ${result.detail || result.error}`);
    } else {
      setHydratedContent(result.content);
      setRequirements([]);
      setView("raw");

      console.log("Phase 5.1 Hydration complete.");

    }
  } catch (error) {
    console.error("Hydration failed:", error);
  } finally {
    setIsReading(false);
  }
};

 const handleInterpretation = async (payload: any) => {
  console.log("Interpretation requested.");

  try {
    const response = await fetch(
      "http://localhost:8000/api/interpret-job",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );

    const result = await response.json();
    console.log("Interpretation response:", result);

    if (response.status !== 200) {
      console.error("Interpretation error:", result.detail);
      return;
    }

    const explicit =
      result.interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

    setRequirements(explicit);
    setView("structured");

    phase6Ref.current?.completeInterpretation();
  } catch (error) {
    console.error("Interpretation failed:", error);
  }
};

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

const articleStyle: React.CSSProperties = {
  maxWidth: "720px",
  margin: "0 auto",
  lineHeight: 1.6,
  fontSize: "16px",
  color: "#222",
};

const renderJobContent = (content: string) => {
  const lines = content.split("\n");

  return (
    <div style={articleStyle}>
      {lines.map((line, index) => {
        const trimmed = line.trim();

        // Empty line = vertical spacing
        if (!trimmed) {
          return <div key={index} style={{ height: "16px" }} />;
        }

        // Treat short standalone lines as section headers
        if (
          trimmed.length < 80 &&
          !trimmed.endsWith(".") &&
          trimmed.split(" ").length < 8
        ) {
          return (
            <h2
              key={index}
              style={{
                marginTop: "32px",
                fontSize: "20px",
                fontWeight: 600,
              }}
            >
              {trimmed}
            </h2>
          );
        }

        return (
          <p key={index} style={{ marginBottom: "12px" }}>
            {trimmed}
          </p>
        );
      })}
    </div>
  );
};

  return (
      <div style={{
          display: "flex",
          height: "100vh",
          overflow: "hidden",   // 🔥 prevents whole-page scroll
          fontFamily: "system-ui, sans-serif"
      }}>      {/* 1. Daily Feed (Left Sidebar) */}
          <aside style={{
              width: "320px",
              borderRight: "1px solid #eee",
              padding: "20px",
              backgroundColor: "#fff",
              overflowY: "auto",    // 🔥 allow independent scroll
              height: "100vh"       // 🔥 fill full viewport
          }}>
              <h2 style={{fontSize: "18px", marginBottom: "20px"}}>Daily Feed</h2>
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
                      <div style={{
                          fontSize: "12px",
                          fontWeight: "bold",
                          color: "#0070f3",
                          marginBottom: "4px"
                      }}>{job.company}</div>
                      <div style={{fontWeight: 600, fontSize: "14px"}}>{job.title}</div>
                  </div>
              ))}
          </aside>

          {/* 2. Main Content Area (Center) */}
          <main style={{
              flex: 1,
              padding: "40px",
              backgroundColor: "#fafafa",
              height: "100vh",       // 🔥 fixed viewport height
              overflowY: "auto",     // 🔥 independent scroll
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
                      {isReading && <p style={{color: "#0070f3"}}><em>System is reading...</em></p>}
                      {userPreviewUrl && !hydratedContent && (
                          <div style={{
                              backgroundColor: "#fff",
                              borderRadius: "12px",
                              border: "1px solid #eee",
                              overflow: "hidden"
                          }}>
                              <div style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                  padding: "12px 16px",
                                  borderBottom: "1px solid #eee"
                              }}>
                                  <div>
                                      <div style={{fontWeight: 700}}>User Preview</div>
                                      <div style={{fontSize: "12px", color: "#666"}}>
                                          This is a server-rendered preview. Hydration requires consent in the right
                                          panel.
                                      </div>
                                  </div>
                                  <button
                                      onClick={() => setUserPreviewUrl(null)}
                                      style={{
                                          border: "1px solid #ddd",
                                          background: "#fff",
                                          borderRadius: "8px",
                                          padding: "8px 12px",
                                          cursor: "pointer"
                                      }}
                                  >
                                      Close
                                  </button>
                              </div>

                              <embed
                                  src={`http://localhost:8000/api/user-preview?url=${encodeURIComponent(userPreviewUrl)}&v=${previewVersion}`}
                                  type="application/pdf"
                                  style={{width: "100%", height: "70vh", border: "0"}}
                              />
                          </div>
                      )}

                      <div style={{marginBottom: "16px"}}>
                          <a
                              href={selectedJob.url}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                  padding: "10px 16px",
                                  borderRadius: "8px",
                                  border: "1px solid #ddd",
                                  color: "#333",
                                  textDecoration: "none",
                                  fontWeight: 600,
                                  background: "#fff"
                              }}
                          >
                              View on Company Site
                          </a>
                      </div>
                      {!hydratedContent ? (
                          <div style={{textAlign: "center", padding: "60px"}}>
                              <h2>{selectedJob.title} at {selectedJob.company}</h2>
                              <p style={{color: "#666"}}>Loading job content…</p>
                          </div>
                      ) : (

                          /* Hydrated Analysis View (Phase 5.1 & 5.2) */
                          <div style={{marginTop: "24px"}}>
                              <div style={{display: "flex", gap: "10px", marginBottom: "16px"}}>

                                  <button
                                      disabled={requirements.length === 0}
                                      onClick={() => setView("structured")}
                                      style={{
                                          ...tabStyle(view === "structured"),
                                          opacity: requirements.length === 0 ? 0.4 : 1,
                                          cursor: requirements.length === 0 ? "not-allowed" : "pointer"
                                      }}
                                  >
                                      {requirements.length === 0
                                          ? "Structured Interpretation (Disabled)"
                                          : "Structured Interpretation (5.2)"}
                                  </button>

                                  <button
                                      onClick={() => setView("raw")}
                                      style={tabStyle(view === "raw")}
                                  >
                                      Raw Content (5.1)
                                  </button>

                              </div>
                              <div style={contentBoxStyle}>
                                  {view === 'raw' ? (
                                      hydratedContent ? renderJobContent(hydratedContent) : null
                                  ) : (
                                      requirements.length > 0 ? (
                                          <ul style={{paddingLeft: "20px"}}>
                                              {requirements.map((req, i) => (
                                                  <li key={i} style={{marginBottom: "12px"}}>
                                                  <div style={{fontWeight: 600}}>
                                                          {req.requirement_text}
                                                      </div>
                                                      <div style={{fontSize: "12px", color: "#666"}}>
                                                          Modality: {req.modality}
                                                      </div>
                                                  </li>
                                              ))}
                                          </ul>
                                      ) : (
                                          <div style={{textAlign: 'center', padding: '40px'}}>
                                              <h3 style={{color: '#333'}}>Waiting for Analysis Authorization</h3>
                                              <p style={{color: '#666'}}>
                                                  Complete the consent flow in the right panel to enable structured
                                                  interpretation.
                                              </p>
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
              <div style={{
                  width: "360px",
                  borderLeft: "1px solid #eee",
                  backgroundColor: "#fff",
                  height: "100vh",
                  overflowY: "auto"   // 🔥 independent scroll
              }}>
                  <Phase6SidePanel
                      ref={phase6Ref}
                      jobId={selectedJob.id}
                      jobTitle={selectedJob.title}
                      onConsentGranted={handleConsentHandoff}
                      onConsentRevoked={handleConsentRevoked}
                  />
              </div>
          )}

      </div>
  );
}