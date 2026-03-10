import React, { useState, useRef, useEffect } from "react";
import { type Phase6SidePanelHandle } from "../phase6/Phase6SidePanel";
import { FeedSidebar } from "../feed/FeedSidebar";
import { isLikelyAiRole, JobCard } from "../feed/JobCard";
import { SavedJobsBoard } from "../feed/SavedJobsBoard";
import { RightPanel } from "../rightpanel/RightPanel";
import {
  buildSignalConstellation,
  CONSTELLATION_GROUP_SIGNALS,
  type ConstellationGroup,
} from "../feed/signal_constellation";

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
const [interpretationResult, setInterpretationResult] = useState<any | null>(null);
const [spanMap, setSpanMap] = useState<Record<string, string>>({});
const [view, setView] = useState<'raw' | 'structured'>('raw')
const [hydrationUiState, setHydrationUiState] = useState<"READY" | "HYDRATION_BLOCKED">("READY");
const [hydrationIncomplete, setHydrationIncomplete] = useState(false);
const [manualRawContent, setManualRawContent] = useState("");
const [additionalContext, setAdditionalContext] = useState("");
    const [isReading, setIsReading] = useState(false);
const [isInterpreting, setIsInterpreting] = useState(false);
const [loadingArtifacts, setLoadingArtifacts] = useState(false);
const [availableJobs, setAvailableJobs] = useState<any[]>([]);
const [locationFilter, setLocationFilter] = useState("");
const [roleFilter, setRoleFilter] = useState("");
const [experienceFilter, setExperienceFilter] = useState("");
const [companyFilter, setCompanyFilter] = useState("");
const [signalsFilter, setSignalsFilter] = useState<string[]>([]);
const [aiOnly, setAiOnly] = useState(false);
const [viewMode, setViewMode] = useState<"feed" | "saved">("feed");
const [page, setPage] = useState(1);
const [pageSize] = useState(50);
const [totalJobs, setTotalJobs] = useState(0);
const phase6Ref = useRef<Phase6SidePanelHandle | null>(null);
const hydrationCache = useRef<Record<string, string>>({});
const interpretationCache = useRef<Record<string, any>>({});
const spanMapCache = useRef<Record<string, Record<string, string>>>({});
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
        if (signalsFilter.length > 0) {
          params.set("signals", signalsFilter.join(","));
        }
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
        first_seen_at: j.first_seen_at,
        posted_at: j.posted_at,
        provider: j.provider,
        state: j.state,
        ai_relevance_score: j.ai_relevance_score,
        raw_provider_payload_json: j.raw_provider_payload_json,
        signals: Array.isArray(j.signals) ? j.signals : [],
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
}, [viewMode, locationFilter, roleFilter, experienceFilter, companyFilter, signalsFilter, page, pageSize]);

useEffect(() => {
  setPage(1);
}, [locationFilter, roleFilter, experienceFilter, companyFilter, signalsFilter]);

useEffect(() => {
  setPage(1);
  setSelectedJob(null);
}, [viewMode]);

const pipelineJobs = PIPELINE_STATES.reduce((acc: Record<string, any[]>, state) => {
  acc[state] = availableJobs.filter((job) => job.state === state);
  return acc;
}, {});
const visibleJobs =
  aiOnly && viewMode === "feed"
    ? availableJobs.filter((job) => isLikelyAiRole(job.title))
    : availableJobs;
const constellation = buildSignalConstellation(visibleJobs);
const CONSTELLATION_LABELS: Record<ConstellationGroup, string> = {
  ai_ml: "AI / ML",
  engineering: "Engineering",
  data: "Data",
  product: "Product",
  security: "Security",
};
const activeConstellation = (Object.keys(CONSTELLATION_GROUP_SIGNALS) as ConstellationGroup[]).find(
  (group) => {
    const expected = CONSTELLATION_GROUP_SIGNALS[group];
    return expected.length === signalsFilter.length && expected.every((signal) => signalsFilter.includes(signal));
  }
);

 // --- Handlers ---
 const handleJobSelect = (job: any) => {
  if (viewMode === "saved" && selectedJob?.id === job.id) {
    setSelectedJob(null);
    return;
  }
  const cachedHydration = hydrationCache.current[job.id];
  phase6Ref.current?.reset();
  setSelectedJob(job);
  if (cachedHydration) {
    setHydratedContent(cachedHydration);
    setHydrationIncomplete(looksIncomplete(cachedHydration));
  } else {
    setHydratedContent(null);
    setHydrationIncomplete(false);
  }
  setIsReading(false);
  setHydrationUiState("READY");
  setManualRawContent("");
  setAdditionalContext("");
  setRequirements([]);
  setInterpretationResult(null);
  setSpanMap({});
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

const applyDomainFilter = (domain: ConstellationGroup) => {
  setViewMode("feed");
  setSignalsFilter(CONSTELLATION_GROUP_SIGNALS[domain]);
  setSelectedJob(null);
  setPage(1);
};

useEffect(() => {
  if (!selectedJob) return;
  const jobId = selectedJob.id;

  const loadArtifacts = async () => {
    setLoadingArtifacts(true);
    try {
      if (hydrationCache.current[jobId]) {
        setHydratedContent(hydrationCache.current[jobId]);
        setHydrationIncomplete(looksIncomplete(hydrationCache.current[jobId]));

        const cachedInterpretation = interpretationCache.current[jobId];
        const cachedSpanMap = spanMapCache.current[jobId];

        if (cachedInterpretation) {
          setInterpretationResult(cachedInterpretation);
          setSpanMap(cachedSpanMap ?? {});
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
        setHydrationIncomplete(looksIncomplete(hydrationData.content));
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
      const fetchedSpanMap =
        interpretationData?.span_map && typeof interpretationData.span_map === "object"
          ? interpretationData.span_map
          : {};
      setSpanMap(fetchedSpanMap);
      spanMapCache.current[jobId] = fetchedSpanMap;

      if (interpretationData?.interpretation) {
        setInterpretationResult(interpretationData.interpretation);
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
    } finally {
      setLoadingArtifacts(false);
    }
  };

  loadArtifacts();

}, [selectedJob]);

  const handleConsentRevoked = async () => {
  setRequirements([]);
  setInterpretationResult(null);
  setSpanMap({});
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
      setHydratedContent(null);
      setHydrationIncomplete(false);
      setHydrationUiState("HYDRATION_BLOCKED");
    } else if (result.content && !isBlockedHydrationContent(result.content)) {
        setHydratedContent(result.content);
        setHydrationIncomplete(looksIncomplete(result.content));
        if (payload?.job_id) {
          hydrationCache.current[payload.job_id] = result.content;
        }
        setHydrationUiState("READY");
        setView("raw");
        console.log("Phase 5.1 Hydration complete.");
    } else {
      setHydratedContent(null);
      setHydrationIncomplete(false);
      setHydrationUiState("HYDRATION_BLOCKED");
    }
  } catch (error) {
    console.error("Hydration failed:", error);
    setHydratedContent(null);
    setHydrationIncomplete(false);
    setHydrationUiState("HYDRATION_BLOCKED");
  } finally {
    setIsReading(false);
  }
};

const handleManualInterpretation = async () => {
  const raw = manualRawContent.trim();
  if (!raw) return;

  setIsInterpreting(true);
  try {
    const res = await fetch(
      "http://localhost:8000/api/interpret-manual",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_content: raw }),
      }
    );

    const result = await res.json();
    if (!res.ok) {
      throw new Error(result?.detail || "Manual interpretation failed");
    }

    const explicit =
      result.interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

    setHydratedContent(raw);
    setHydrationIncomplete(looksIncomplete(raw));
    setHydrationUiState("READY");
    if (selectedJob?.id) {
      hydrationCache.current[selectedJob.id] = raw;
    }
    setManualRawContent("");
    setInterpretationResult(result.interpretation ?? null);
    if (result?.span_map && typeof result.span_map === "object" && selectedJob?.id) {
      setSpanMap(result.span_map);
      spanMapCache.current[selectedJob.id] = result.span_map;
    }
    setRequirements(explicit);
    setView("structured");
    phase6Ref.current?.completeInterpretation();
  } catch (error) {
    console.error("Manual interpretation failed:", error);
  } finally {
    setIsInterpreting(false);
  }
};

const handleReinterpretWithContext = async () => {
  if (!additionalContext.trim()) return;

  const combinedContent =
    (hydratedContent || "") +
    "\n\n--- USER ADDED CONTEXT ---\n\n" +
    additionalContext;

  setIsInterpreting(true);
  try {
    const res = await fetch("http://localhost:8000/api/interpret-manual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_content: combinedContent }),
    });

    const result = await res.json();
    if (!res.ok) {
      throw new Error(result?.detail || "Re-interpretation with context failed");
    }

    const interpretation = result.interpretation ?? null;
    const explicit = interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

    setInterpretationResult(interpretation);
    setRequirements(explicit);

    if (result?.span_map && typeof result.span_map === "object") {
      setSpanMap(result.span_map);
      if (selectedJob?.id) {
        spanMapCache.current[selectedJob.id] = result.span_map;
      }
    } else {
      setSpanMap({});
      if (selectedJob?.id) {
        spanMapCache.current[selectedJob.id] = {};
      }
    }

    if (selectedJob?.id) {
      interpretationCache.current[selectedJob.id] = interpretation;
    }

    setHydratedContent(combinedContent);
    setHydrationIncomplete(looksIncomplete(combinedContent));
    if (selectedJob?.id) {
      hydrationCache.current[selectedJob.id] = combinedContent;
    }
    setView("structured");
    phase6Ref.current?.completeInterpretation();
  } catch (error) {
    console.error("Re-interpretation with context failed:", error);
  } finally {
    setIsInterpreting(false);
  }
};

 const handleInterpretation = async (payload: any) => {
  console.log("Interpretation requested.");
  setIsInterpreting(true);

  try {
    const res = await fetch(
      "http://localhost:8000/api/interpret-job",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );

    const result = await res.json();
    console.log("Interpretation response:", result);

    if (!res.ok) {
      throw new Error(result?.detail || "Interpretation failed");
    }

    const explicit =
      result.interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

    setInterpretationResult(result.interpretation ?? null);
    if (result?.span_map && typeof result.span_map === "object" && selectedJob?.id) {
      setSpanMap(result.span_map);
      spanMapCache.current[selectedJob.id] = result.span_map;
    }
    setRequirements(explicit);
    setView("structured");

    phase6Ref.current?.completeInterpretation();
  } catch (error) {
    console.error("Interpretation failed:", error);
    phase6Ref.current?.reset();
  } finally {
    setIsInterpreting(false);
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

const skeletonLine: React.CSSProperties = {
  height: "14px",
  backgroundColor: "#eee",
  borderRadius: "6px",
  marginBottom: "12px",
  animation: "pulse 1.5s infinite ease-in-out"
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

function isBlockedHydrationContent(content: string | null | undefined): boolean {
  if (!content) return false;

  const text = content.toLowerCase();
  const patterns = [
    "sorry, you have been blocked",
    "you are unable to access",
    "performance & security by cloudflare",
    "attention required!",
    "checking your browser before accessing",
    "cloudflare ray id",
    "why have i been blocked?",
  ];

  return patterns.some((pattern) => text.includes(pattern));
}

function looksIncomplete(content: string): boolean {
  if (!content) return true;

  const text = content.toLowerCase();

  const navSignals = [
    "privacy policy",
    "terms",
    "contact us",
    "press",
    "careers",
    "blog",
    "resources",
    "help",
    "©"
  ];

  let navHits = 0;

  navSignals.forEach(signal => {
    if (text.includes(signal)) navHits++;
  });

  const shortContent = content.length < 1200;

  return shortContent || navHits >= 3;
}

const resolveEvidenceTexts = (spanIds: string[] = []): string[] => {
  const seen = new Set<string>();
  const texts: string[] = [];
  for (const id of spanIds) {
    const text = spanMap[id];
    if (!text || seen.has(text)) continue;
    seen.add(text);
    texts.push(text);
  }
  return texts;
};

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        padding: "16px",
        marginBottom: "20px",
        background: "#ffffff",
        boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
      }}
    >
      <div
        style={{
          fontWeight: 600,
          fontSize: "15px",
          marginBottom: "12px",
          color: "#222",
        }}
      >
        {title}
      </div>

      {children}
    </div>
  );
}

function EvidenceBlock({ spanIds }: { spanIds: string[] }) {
  const [open, setOpen] = React.useState(false);
  const evidenceTexts = resolveEvidenceTexts(spanIds);

  if (evidenceTexts.length === 0) return null;

  return (
    <div style={{ marginTop: "6px" }}>
      <div
        style={{
          fontSize: "12px",
          fontWeight: 600,
          color: "#666",
          cursor: "pointer",
          userSelect: "none",
        }}
        onClick={() => setOpen(!open)}
      >
        Evidence ({evidenceTexts.length}) {open ? "▲" : "▼"}
      </div>

      {open && (
        <ul style={{ marginTop: "6px", paddingLeft: "18px" }}>
          {evidenceTexts.map((text, i) => (
            <li
              key={i}
              style={{
                fontSize: "13px",
                color: "#555",
                marginBottom: "4px",
                lineHeight: "1.4",
              }}
            >
              {text}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const totalPages = Math.max(1, Math.ceil(totalJobs / pageSize));

  return (
      <>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 1; }
          100% { opacity: 0.6; }
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
                      ? visibleJobs.filter((job) =>
                          SAVED_STATES.includes(job.state ?? "")
                      )
                      : visibleJobs
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
                  signals: signalsFilter,
                  aiOnly,
              }}
              setFilters={{
                  setLocationFilter,
                  setRoleFilter,
                  setCompanyFilter,
                  setExperienceFilter,
                  setSignalsFilter,
                  setAiOnly,
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
                  <SavedJobsBoard
                      jobsByState={pipelineJobs}
                      selectedJob={selectedJob}
                      onSelectJob={handleJobSelect}
                      onSaveJob={handleSaveJob}
                      onUpdateJobState={handleUpdateJobState}
                  />
              ) : !selectedJob ? (
                  <div style={{ marginTop: "40px", color: "#333" }}>
                      <h1 style={{ marginBottom: "8px" }}>Explore Roles</h1>
                      <p style={{ color: "#666", marginBottom: "20px" }}>
                        Explore matching roles or select a job to analyze.
                      </p>
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(3, 1fr)",
                          gap: "12px",
                        }}
                      >
                        {([
                          "engineering",
                          "ai_ml",
                          "data",
                          "product",
                          "security",
                        ] as ConstellationGroup[]).map((domain) => (
                          <div
                            key={domain}
                            onClick={() => applyDomainFilter(domain)}
                            style={{
                              padding: "16px",
                              borderRadius: "10px",
                              border: "1px solid #eee",
                              cursor: "pointer",
                              background: "#fafafa",
                            }}
                          >
                            <div style={{ fontWeight: 600 }}>
                              {domain === "ai_ml" ? "AI / ML" : domain.replace("_", " ").toUpperCase()} ({constellation[domain].length})
                            </div>
                            <div style={{ fontSize: "12px", color: "#777" }}>
                              Explore roles
                            </div>
                          </div>
                        ))}
                      </div>
                      {viewMode === "feed" && (
                        <div style={{ marginTop: "20px" }}>
                          {activeConstellation && (
                            <div style={{ fontSize: "13px", color: "#666", marginBottom: "10px" }}>
                              Exploring: {CONSTELLATION_LABELS[activeConstellation]}
                            </div>
                          )}
                          {visibleJobs.length > 0 ? (
                            <div>
                              {visibleJobs.map((job: any) => (
                                <JobCard
                                  key={job.id}
                                  job={job}
                                  selected={false}
                                  onClick={() => handleJobSelect(job)}
                                  onSave={() => handleSaveJob(job.id, job.state)}
                                />
                              ))}
                            </div>
                          ) : (
                            <div style={{ fontSize: "13px", color: "#777" }}>
                              No jobs match the current filters.
                            </div>
                          )}
                        </div>
                      )}
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
                      {hydrationUiState === "HYDRATION_BLOCKED" ? (
                          <div
                              style={{
                                  background: "#fff",
                                  border: "1px solid #eee",
                                  borderRadius: "12px",
                                  padding: "20px",
                              }}
                          >
                              <h2 style={{ marginTop: 0 }}>This job posting can't be automatically loaded.</h2>
                              <p style={{ color: "#666", marginBottom: "14px" }}>
                                  Some job sites block automated access.
                                  <br />
                                  You can still analyze the role by pasting the job description below.
                              </p>
                              <textarea
                                  value={manualRawContent}
                                  onChange={(e) => setManualRawContent(e.target.value)}
                                  placeholder="Paste the full job description here. Include responsibilities, requirements, and any role details you want analyzed."
                                  style={{
                                      width: "100%",
                                      minHeight: "220px",
                                      padding: "12px",
                                      border: "1px solid #ddd",
                                      borderRadius: "8px",
                                      resize: "vertical",
                                      fontFamily: "inherit",
                                      fontSize: "14px",
                                      lineHeight: 1.4,
                                      marginBottom: "12px",
                                  }}
                              />
                              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                                  <button
                                      onClick={handleManualInterpretation}
                                      disabled={!manualRawContent.trim() || isInterpreting}
                                      style={{
                                          padding: "10px 16px",
                                          borderRadius: "8px",
                                          border: "1px solid #ddd",
                                          background: "#fff",
                                          fontWeight: 600,
                                          cursor: !manualRawContent.trim() || isInterpreting ? "not-allowed" : "pointer",
                                          opacity: !manualRawContent.trim() || isInterpreting ? 0.6 : 1,
                                      }}
                                  >
                                      Analyze Role
                                  </button>
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
                                          background: "#fff",
                                      }}
                                  >
                                      Open Job Page
                                  </a>
                              </div>
                          </div>
                      ) : !hydratedContent ? (
                          <div style={{textAlign: "center", padding: "60px"}}>
                              <h2>{selectedJob.title} at {selectedJob.company}</h2>
                              {isReading && (
                                <div>
                                  {Array.from({ length: 12 }).map((_, i) => (
                                    <div key={i} style={skeletonLine}></div>
                                  ))}
                                </div>
                              )}
                          </div>
                      ) : (

                          /* Hydrated Analysis View (Phase 5.1 & 5.2) */
                          <div style={{marginTop: "24px"}}>
                              <div style={{display: "flex", gap: "10px", marginBottom: "16px"}}>

                                  <button
                                      disabled={!interpretationResult}
                                      onClick={() => setView("structured")}
                                      style={{
                                          ...tabStyle(view === "structured"),
                                          opacity: interpretationResult ? 1 : 0.4,
                                          cursor: interpretationResult ? "pointer" : "not-allowed"
                                      }}
                                  >
                                      {!interpretationResult
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
                              {view === 'raw' ? (
                                  <div>
                                      <div style={contentBoxStyle}>
                                          {hydratedContent ? renderJobContent(hydratedContent) : null}
                                      </div>
                                  </div>
                              ) : (
                                  <div
                                      style={{
                                          background: "#f5f6f8",
                                          height: "100%",
                                          overflowY: "auto",
                                          padding: "24px",
                                          borderRadius: "12px",
                                      }}
                                  >
                                      <div
                                          style={{
                                              maxWidth: "760px",
                                              margin: "0 auto",
                                          }}
                                      >
                                          {interpretationResult ? (
                                              <div style={{display: "grid", gap: "0px"}}>
                                                  <Card title="Role Summary">
                                                      <p style={{margin: 0, color: "#333"}}>
                                                          {interpretationResult?.RoleSummary?.summary_text ?? "No role summary provided."}
                                                      </p>
                                                      <EvidenceBlock spanIds={interpretationResult?.RoleSummary?.evidence_span_ids ?? []} />
                                                  </Card>

                                                  <Card title="Requirements">
                                                      {requirements.length > 0 ? (
                                                          <div>
                                                              {requirements.map((req, i) => (
                                                                  <div key={i} style={{ marginBottom: "12px" }}>
                                                                      <div style={{ fontSize: "14px", fontWeight: 500 }}>
                                                                          {req.requirement_text}
                                                                      </div>
                                                                      <div
                                                                          style={{
                                                                              fontSize: "12px",
                                                                              color: "#6b7280",
                                                                              marginTop: "2px",
                                                                          }}
                                                                      >
                                                                          Modality: {req.modality}
                                                                      </div>
                                                                      <EvidenceBlock spanIds={req.source_span_id ? [req.source_span_id] : []} />
                                                                  </div>
                                                              ))}
                                                          </div>
                                                      ) : (
                                                          <p style={{margin: 0, color: "#666"}}>No explicit requirements provided.</p>
                                                      )}
                                                  </Card>

                                                  <Card title="Implicit Signals">
                                                      {(interpretationResult?.RequirementsAnalysis?.implicit_signals ?? []).length > 0 ? (
                                                          <div style={{display: "grid", gap: "10px"}}>
                                                              {(interpretationResult?.RequirementsAnalysis?.implicit_signals ?? []).map((signal: any, i: number) => (
                                                                  <div key={i}>
                                                                      <div style={{fontSize: "14px", color: "#444"}}>{signal.signal_text}</div>
                                                                      <EvidenceBlock spanIds={signal.evidence_span_ids ?? []} />
                                                                  </div>
                                                              ))}
                                                          </div>
                                                      ) : (
                                                          <p style={{margin: 0, color: "#666"}}>No implicit signals provided.</p>
                                                      )}
                                                  </Card>

                                                  <Card title="Capability Emphasis">
                                                      {(interpretationResult?.CapabilityEmphasisSignals ?? []).length > 0 ? (
                                                          <div style={{display: "grid", gap: "12px"}}>
                                                              {(interpretationResult?.CapabilityEmphasisSignals ?? []).map((signal: any, i: number) => (
                                                                  <div key={i}>
                                                                      <div style={{fontWeight: 500}}>🧠 {signal.domain_label}</div>
                                                                      <div style={{fontSize: "14px", color: "#444"}}>{signal.description}</div>
                                                                      <EvidenceBlock spanIds={signal.evidence_span_ids ?? []} />
                                                                  </div>
                                                              ))}
                                                          </div>
                                                      ) : (
                                                          <p style={{margin: 0, color: "#666"}}>No capability emphasis signals provided.</p>
                                                      )}
                                                  </Card>

                                                  <Card title="Project Opportunities">
                                                      {(interpretationResult?.ProjectOpportunitySignals ?? []).length > 0 ? (
                                                          <div style={{display: "grid", gap: "12px"}}>
                                                              {(interpretationResult?.ProjectOpportunitySignals ?? []).map((signal: any, i: number) => (
                                                                  <div key={i}>
                                                                      <div style={{fontWeight: 600}}>{signal.capability_surface}</div>
                                                                      <div style={{fontSize: "14px", color: "#444"}}>{signal.description}</div>
                                                                      <EvidenceBlock spanIds={signal.evidence_span_ids ?? []} />
                                                                  </div>
                                                              ))}
                                                          </div>
                                                      ) : (
                                                          <p style={{margin: 0, color: "#666"}}>No project opportunity signals provided.</p>
                                                      )}
                                                  </Card>
                                              </div>
                                          ) : (
                                              <div style={{textAlign: 'center', padding: '40px'}}>
                                                  <h3 style={{color: '#333'}}>Waiting for Analysis Authorization</h3>
                                                  <p style={{color: '#666'}}>
                                                      Complete the consent flow in the right panel to enable structured
                                                      interpretation.
                                                  </p>
                                              </div>
                                          )}
                                      </div>
                                  </div>
                              )}
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
                  <RightPanel
                      ref={phase6Ref}
                      jobId={selectedJob.id}
                      jobTitle={selectedJob.title}
                      loadingArtifacts={loadingArtifacts}
                      additionalContext={additionalContext}
                      setAdditionalContext={setAdditionalContext}
                      handleReinterpretWithContext={handleReinterpretWithContext}
                      isInterpreting={isInterpreting}
                      hydrationIncomplete={hydrationIncomplete}
                      onConsentGranted={handleConsentHandoff}
                      onConsentRevoked={handleConsentRevoked}
                  />
              </div>
          )}

      </div>
      </>
  );
}
