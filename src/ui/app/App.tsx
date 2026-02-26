import React, { useState, useRef } from "react";
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
  const [view, setView] = useState<'raw' | 'structured'>('raw');
  const [isReading, setIsReading] = useState(false);
  const [availableJobs] = useState([
  {
    id: "greenhouse:stripe:7409686",
    title: "Software Engineer, Product",
    company: "Stripe",
    url: "https://boards.greenhouse.io/stripe/jobs/7409686"
  }
]);
  const phase6Ref = useRef<Phase6SidePanelHandle | null>(null);
  const [userPreviewUrl, setUserPreviewUrl] = useState<string | null>(null);
  const [previewVersion, setPreviewVersion] = useState(0);
  // --- Handlers ---
  const handleJobSelect = (job: any) => {
    setSelectedJob(job);
    // CRITICAL: Reset hydration when switching jobs to maintain the "Wall"
    setHydratedContent(null);
    setRequirements([]);
    setView('raw');
    setUserPreviewUrl(null);

    phase6Ref.current?.reset();
  };

  const handleConsentRevoked = () => {
    setHydratedContent(null);
    setRequirements([]);
    setView("raw");
    setUserPreviewUrl(null);
  };
 const handleConsentHandoff = async (payload: any) => {
  console.log("Phase 6 Handoff Emitted:", payload);

  const scope = payload?.consent?.scope;

  if (!scope) {
    console.error("Missing consent scope.");
    return;
  }

  if (scope === "hydrate") {
    await handleHydration(payload);
    return;
  }

  if (scope === "interpret_job_posting") {
    await handleInterpretation(payload);
    return;
  }

  console.error("Unknown consent scope:", scope);
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
      phase6Ref.current?.completeHydration();
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
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#0070f3", marginBottom: "4px" }}>{job.company}</div>
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
                        This is a server-rendered preview. Hydration requires consent in the right panel.
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


            {!hydratedContent ? (
                /* The Choice Gate - Structural Honesty */
                <div style={{
                  textAlign: "center",
                  padding: "60px",
                  backgroundColor: "#fff", borderRadius: "12px", border: "1px solid #eee" }}>
    <h2 style={{ color: "#333" }}>{selectedJob.title} at {selectedJob.company}</h2>
    <p style={{ color: "#666", marginBottom: "32px" }}>How would you like to explore this role?</p>

    <div style={{display: "flex", gap: "20px", justifyContent: "center"}}>
      <button
          onClick={() => {setUserPreviewUrl(selectedJob.url); setPreviewVersion(v => v + 1);}}
          style={{
            padding: "16px 24px",
            borderRadius: "8px",
            border: "1px solid #ddd",
            color: "#333",
            background: "#fff",
            cursor: "pointer",
            fontWeight: "bold"
          }}
      >
        Preview in App (User-only)
        <div style={{fontWeight: "normal", fontSize: "12px", marginTop: "4px", color: "#666"}}>
          Opens the live listing here. The system still has not read it.
        </div>
      </button>

      <button
          onClick={() => {
            phase6Ref.current?.requestHydration();
          }}
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
          I will fetch and display the job posting here. Interpretation requires explicit consent in the right panel.
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
                <div style={{marginTop: "24px"}}>
                  <div style={{display: "flex", gap: "10px", marginBottom: "16px"}}>
                    <button disabled style={{opacity: 0.4}}>
                      Structured Interpretation (Disabled)
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
                 Complete the consent flow in the right panel to enable structured interpretation.
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
         <Phase6SidePanel
            ref={phase6Ref}
            jobId={selectedJob.id}
            jobTitle={selectedJob.title}
            onConsentGranted={handleConsentHandoff}
            onConsentRevoked={handleConsentRevoked}
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