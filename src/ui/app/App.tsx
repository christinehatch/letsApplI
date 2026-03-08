import React, { useState, useRef, useEffect } from "react";
import { Phase6SidePanel, type Phase6SidePanelHandle } from "../phase6/Phase6SidePanel";
import { FeedSidebar } from "../feed/FeedSidebar";
import { JobCard } from "../feed/JobCard";

const PIPELINE_STATES = ["saved", "applied", "interview", "offer"];
const SAVED_STATES = PIPELINE_STATES;

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
const [isInterpreting, setIsInterpreting] = useState(false);
const [availableJobs, setAvailableJobs] = useState<any[]>([]);
const [locationFilter, setLocationFilter] = useState("");
const [roleFilter, setRoleFilter] = useState("");
const [experienceFilter, setExperienceFilter] = useState("");
const [companyFilter, setCompanyFilter] = useState("");
const [viewMode, setViewMode] = useState<"feed" | "saved">("feed");
const [page, setPage] = useState(1);
const [pageSize] = useState(50);
const [totalJobs, setTotalJobs] = useState(0);
const phase6Ref = useRef<Phase6SidePanelHandle | null>(null);
const hydrationCache = useRef<Record<string, string>>({});
const interpretationCache = useRef<Record<string, any>>({});
const [userPreviewUrl, setUserPreviewUrl] = useState<string | null>(null);
const [previewVersion, setPreviewVersion] = useState(0);

useEffect(() => {
  const fetchJobs = async () => {
    try {
      let res;
      if (viewMode === "feed") {
        const params = new URLSearchParams();
        if (locationFilter.trim()) params.set("location", locationFilter.trim());
        if (roleFilter.trim()) params.set("role", roleFilter.trim());
        if (experienceFilter.trim()) params.set("experience", experienceFilter.trim());
        if (companyFilter.trim()) params.set("company", companyFilter.trim());
        params.set("page", String(page));
        params.set("page_size", String(pageSize));
        const query = params.toString();

        res = await fetch(
          `http://localhost:8000/api/discovery-feed${query ? `?${query}` : ""}`
        );
      } else {
        res = await fetch("http://localhost:8000/api/saved-jobs");
      }

      const data = await res.json();
      setTotalJobs(viewMode === "feed" ? (data.total_jobs ?? 0) : (data.jobs?.length ?? 0));

      const jobs = data.jobs.map((j: any) => ({
        id: j.job_id,
        title: j.title,
        company: j.company,
        location: j.location,
        url: j.url,
        posted_at: j.posted_at,
        provider: j.provider,
        state: j.state,
      }));

      setAvailableJobs(
        viewMode === "saved"
          ? jobs.filter((job: any) => SAVED_STATES.includes(job.state ?? ""))
          : jobs
      );
    } catch (err) {
      console.error("Failed to load discovery feed:", err);
    }
  };

  fetchJobs();
}, [viewMode, locationFilter, roleFilter, experienceFilter, companyFilter, page, pageSize]);

useEffect(() => {
  setPage(1);
}, [locationFilter, roleFilter, experienceFilter, companyFilter]);

useEffect(() => {
  setPage(1);
  setSelectedJob(null);
}, [viewMode]);

const pipelineJobs = PIPELINE_STATES.reduce((acc: Record<string, any[]>, state) => {
  acc[state] = availableJobs.filter((job) => job.state === state);
  return acc;
}, {});

 // --- Handlers ---
 const handleJobSelect = (job: any) => {
  if (viewMode === "saved" && selectedJob?.id === job.id) {
    setSelectedJob(null);
    return;
  }
  phase6Ref.current?.reset();
  setSelectedJob(job);
  setHydratedContent(null);
  setRequirements([]);
  setView("raw");
  setUserPreviewUrl(null);
};

 const handleUpdateJobState = async (jobId: string, newState: string) => {
  try {
    const response = await fetch(
      "http://localhost:8000/api/job-state",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobId, state: newState }),
      }
    );

    if (!response.ok) {
      const err = await response.json();
      console.error("Failed to update job state:", err.detail || err);
      return;
    }

    setAvailableJobs((prev) => {
      const updated = prev
        .map((job) =>
          job.id === jobId ? { ...job, state: newState } : job
        );
      if (viewMode === "saved") {
        return updated.filter((job) =>
          SAVED_STATES.includes(job.state ?? "")
        );
      }
      return updated;
    });

    setSelectedJob((prev: any) => {
      if (!prev || prev.id !== jobId) {
        return prev;
      }
      if (viewMode === "saved" && !SAVED_STATES.includes(newState)) {
        return null;
      }
      return { ...prev, state: newState };
    });
  } catch (error) {
    console.error("Failed to update job state:", error);
  }
};

 const handleSaveJob = async (jobId: string, currentState?: string | null) => {
  const targetState = currentState === "saved" ? "archived" : "saved";
  await handleUpdateJobState(jobId, targetState);
};

useEffect(() => {
  if (!selectedJob) return;
  const jobId = selectedJob.id;

  const loadArtifacts = async () => {
    if (hydrationCache.current[jobId]) {
      setHydratedContent(hydrationCache.current[jobId]);

      const cachedInterpretation = interpretationCache.current[jobId];

      if (cachedInterpretation) {
        phase6Ref.current?.restoreInterpreted(cachedInterpretation);

        const explicit =
          cachedInterpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

        setRequirements(explicit);
        setView("structured");
      }

      return;
    }

    const hydrationRes = await fetch(
      `/api/hydrated-job?job_id=${encodeURIComponent(jobId)}`
    );

    const hydrationData = await hydrationRes.json();

    if (hydrationData?.content) {
      setHydratedContent(hydrationData.content);
      hydrationCache.current[jobId] = hydrationData.content;
    } else {
      const hydratePayload = {
        job_id: jobId,
        consent: {
          granted: true,
          scope: "hydrate",
          granted_at: new Date().toISOString(),
        },
      };

      await handleHydration(hydratePayload);
    }

    const interpretationRes = await fetch(
      `/api/job-interpretation?job_id=${encodeURIComponent(jobId)}`
    );
    const interpretationData = await interpretationRes.json();

    if (interpretationData?.interpretation) {
      interpretationCache.current[jobId] = interpretationData.interpretation;
      phase6Ref.current?.restoreInterpreted(
        interpretationData.interpretation
      );

      const explicit =
        interpretationData.interpretation
          ?.RequirementsAnalysis
          ?.explicit_requirements ?? [];

      setRequirements(explicit);
      setView("structured");
    }
  };

  loadArtifacts();

}, [selectedJob]);

  const handleConsentRevoked = async () => {
  setRequirements([]);
  setView("raw");
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
  setIsInterpreting(true);

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
    setIsInterpreting(false);
  } catch (error) {
    setIsInterpreting(false);
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

const spinnerStyle: React.CSSProperties = {
  width: "18px",
  height: "18px",
  border: "3px solid #eee",
  borderTop: "3px solid #0070f3",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
  marginRight: "10px"
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

const totalPages = Math.max(1, Math.ceil(totalJobs / pageSize));

  return (
      <>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <div style={{
          display: "flex",
          height: "100vh",
          overflow: "hidden",   // 🔥 prevents whole-page scroll
          fontFamily: "system-ui, sans-serif"
      }}>
          {/* 1. Daily Feed (Left Sidebar) */}
          <FeedSidebar
              jobs={
                  viewMode === "saved"
                      ? availableJobs.filter((job) =>
                          SAVED_STATES.includes(job.state ?? "")
                      )
                      : availableJobs
              }
              selectedJob={selectedJob}
              onSelectJob={handleJobSelect}
              onSaveJob={handleSaveJob}
              viewMode={viewMode}
              setViewMode={setViewMode}
              filters={{
                  location: locationFilter,
                  role: roleFilter,
                  company: companyFilter,
                  experience: experienceFilter,
              }}
              setFilters={{
                  setLocationFilter,
                  setRoleFilter,
                  setCompanyFilter,
                  setExperienceFilter,
              }}
              page={page}
              setPage={setPage}
              totalPages={totalPages}
          />

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
              {viewMode === "saved" && !selectedJob ? (
                  <div
                      style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(4, 1fr)",
                          gap: "12px",
                      }}
                  >
                      {PIPELINE_STATES.map((state) => (
                          <div
                              key={state}
                              style={{
                                  background: "#fafafa",
                                  border: "1px solid #eee",
                                  borderRadius: "8px",
                                  padding: "10px",
                              }}
                          >
                              <h4 style={{ marginBottom: "10px", textTransform: "capitalize" }}>
                                  {state}
                              </h4>
                              {pipelineJobs[state]?.map((job) => (
                                  <JobCard
                                      key={job.id}
                                      job={job}
                                      selected={selectedJob?.id === job.id}
                                      onClick={() => handleJobSelect(job)}
                                      onSave={() => handleSaveJob(job.id, job.state)}
                                  />
                              ))}
                          </div>
                      ))}
                  </div>
              ) : !selectedJob ? (
                  <div style={{textAlign: "center", marginTop: "100px", color: "#666"}}>
                      <h1>letsA(ppl)I Discovery</h1>
                      <p>Select a job from your daily feed to begin exploration.</p>
                  </div>
              ) : (
                  <>
                      {viewMode === "saved" && (
                          <button
                              onClick={() => setSelectedJob(null)}
                              style={{
                                  alignSelf: "flex-start",
                                  marginBottom: "12px",
                                  border: "1px solid #ddd",
                                  background: "#fff",
                                  borderRadius: "8px",
                                  padding: "8px 12px",
                                  cursor: "pointer",
                                  fontWeight: 600,
                              }}
                          >
                              ← Back to pipeline
                          </button>
                      )}
                      {isReading && (
                        <div style={{ display: "flex", alignItems: "center", marginBottom: "12px", color: "#0070f3", fontWeight: 500 }}>
                          <div style={spinnerStyle}></div>
                          Hydrating job posting...
                        </div>
                      )}
                      {isInterpreting && (
                        <div style={{ display: "flex", alignItems: "center", marginBottom: "12px", color: "#7c3aed", fontWeight: 500 }}>
                          <div style={spinnerStyle}></div>
                          Analyzing role structure...
                        </div>
                      )}
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
                          <button
                              onClick={() => handleSaveJob(selectedJob.id, selectedJob.state)}
                              style={{
                                  padding: "10px 16px",
                                  borderRadius: "8px",
                                  border: "1px solid #ddd",
                                  color: selectedJob.state === "saved" ? "#7a5a00" : "#333",
                                  textDecoration: "none",
                                  fontWeight: 600,
                                  background: "#fff",
                                  marginRight: "8px",
                                  cursor: "pointer"
                              }}
                          >
                              {selectedJob.state === "saved" ? "★ Saved" : "⭐ Save Job"}
                          </button>
                          <label style={{ marginRight: "8px", color: "#555", fontSize: "14px" }}>
                              Status
                          </label>
                          <select
                              value={selectedJob.state ?? "saved"}
                              onChange={(e) => handleUpdateJobState(selectedJob.id, e.target.value)}
                              style={{
                                  padding: "10px 12px",
                                  borderRadius: "8px",
                                  border: "1px solid #ddd",
                                  background: "#fff",
                                  marginRight: "8px",
                              }}
                          >
                              <option value="saved">Saved</option>
                              <option value="applied">Applied</option>
                              <option value="interview">Interview</option>
                              <option value="offer">Offer</option>
                              <option value="rejected">Rejected</option>
                              <option value="archived">Archived</option>
                          </select>
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
      </>
  );
}
