import React, { useState } from "react";
import { Phase6SidePanel } from "../phase6/Phase6SidePanel";

export function App() {
  const [hydratedContent, setHydratedContent] = useState<string | null>(null);
  const [requirements, setRequirements] = useState<string[]>([]);
  const [view, setView] = useState<'raw' | 'structured'>('raw');
  const [isReading, setIsReading] = useState(false);
  const [availableJobs] = useState([{ id: "stripe:7409686", title: "Software Engineer, Product", company: "Stripe" }]);

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
        // Hydrate Phase 5.1 (Raw) and Phase 5.2 (Structured)
        setHydratedContent(result.content);
        setRequirements(result.requirements || []);

        // Auto-switch to the structured view to show the Interpreter's work
        setView('structured');
        console.log("Phase 5.1 & 5.2 Hydration Complete.");
      }
    } catch (error) {
      console.error("CLI Bridge Handoff failed:", error);
      setHydratedContent("Failed to connect to the backend bridge.");
    } finally {
      setIsReading(false);
    }
  };

  return (
      <div style={{display: "flex", height: "100vh", fontFamily: "system-ui, sans-serif"}}>
        <aside style={{
          width: "320px",
          borderRight: "1px solid #eee",
          padding: "20px",
          backgroundColor: "#fff",
          overflowY: "auto"
        }}>
          <h2 style={{fontSize: "18px", marginBottom: "20px"}}>Daily Feed</h2>
          {availableJobs.map(job => (
              <div
                  key={job.id}
                  style={{
                    padding: "16px",
                    border: "2px solid #0070f3",
                    borderRadius: "12px",
                    marginBottom: "12px",
                    cursor: "default"
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

          <main style={{flex: 1, padding: "40px", backgroundColor: "#fafafa", overflowY: "auto"}}>
            <h1>letsA(ppl)I Discovery</h1>
            <p style={{color: "#666"}}>Select a job from your daily feed to begin exploration.</p>

            {isReading && <p style={{color: "#0070f3"}}><em>System is reading and interpreting job content...</em></p>}

            {hydratedContent && (
                <div style={{marginTop: "24px"}}>
                  {/* View Switcher Tabs */}
                  <div style={{display: "flex", gap: "10px", marginBottom: "16px"}}>
                    <button
                        onClick={() => setView('structured')}
                        style={{
                          padding: "8px 16px",
                          borderRadius: "20px",
                          border: "none",
                          backgroundColor: view === 'structured' ? "#0070f3" : "#eee",
                          color: view === 'structured' ? "#fff" : "#333",
                          cursor: "pointer",
                          fontWeight: 600
                        }}
                    >
                      Structured Interpretation (5.2)
                    </button>
                    <button
                        onClick={() => setView('raw')}
                        style={{
                          padding: "8px 16px",
                          borderRadius: "20px",
                          border: "none",
                          backgroundColor: view === 'raw' ? "#0070f3" : "#eee",
                          color: view === 'raw' ? "#fff" : "#333",
                          cursor: "pointer",
                          fontWeight: 600
                        }}
                    >
                      Raw Content (5.1)
                    </button>
                  </div>

                  <div style={{
                    padding: "24px",
                    border: "1px solid #0070f3",
                    borderRadius: "12px",
                    backgroundColor: "#fff",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.05)"
                  }}>
                    {view === 'raw' ? (
                        <>
                          <h3 style={{marginTop: 0, color: "#0070f3"}}>Phase 5.1: Raw Job Text</h3>
                          <pre style={{whiteSpace: "pre-wrap", fontSize: "14px", lineHeight: "1.6", color: "#333"}}>
                    {hydratedContent}
                  </pre>
                        </>
                    ) : (
                        <>
                          <h3 style={{marginTop: 0, color: "#0070f3"}}>Phase 5.2: Extracted Requirements</h3>
                          <ul style={{paddingLeft: "20px", color: "#333"}}>
                            {requirements.map((req, index) => (
                                <li key={index} style={{marginBottom: "12px", lineHeight: "1.4"}}>{req}</li>
                            ))}
                            {requirements.length === 0 && <li>No specific requirements identified yet.</li>}
                          </ul>
                        </>
                    )}
                  </div>
                </div>
            )}
          </main>

          <Phase6SidePanel
              jobId="stripe:7409686"
              jobTitle="Software Engineer, Product"
              onConsentGranted={handleConsentHandoff}
          />
      </div>
);
}