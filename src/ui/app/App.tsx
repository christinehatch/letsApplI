import React, { useState, useRef, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { type Phase6SidePanelHandle } from "../phase6/Phase6SidePanel";
import { FeedSidebar } from "../feed/FeedSidebar";
import { isLikelyAiRole } from "../feed/JobCard";
import { SavedJobsBoard } from "../feed/SavedJobsBoard";
import { RightPanel } from "../rightpanel/RightPanel";
import MarketJobGrid from "../components/MarketJobGrid";
import { CenterPanelShell } from "./CenterPanelShell";

const PIPELINE_STATES = ["saved", "applied", "interview", "offer"];
const SAVED_STATES = PIPELINE_STATES;

export function App() {
  // --- State ---
  const [searchParams, setSearchParams] = useSearchParams();
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
const [viewMode, setViewMode] = useState<"feed" | "saved">("feed");
const pageSize = 50;
const [totalJobs, setTotalJobs] = useState(0);
const phase6Ref = useRef<Phase6SidePanelHandle | null>(null);
const mainContentRef = useRef<HTMLElement | null>(null);
const jobDescriptionRef = useRef<HTMLDivElement | null>(null);
const hydrationCache = useRef<Record<string, string>>({});
const interpretationCache = useRef<Record<string, any>>({});
const spanMapCache = useRef<Record<string, Record<string, string>>>({});
const interpretationRequestInFlight = useRef<string | null>(null);
const [userPreviewUrl, setUserPreviewUrl] = useState<string | null>(null);
const [previewVersion, setPreviewVersion] = useState(0);
const [marketAlignment, setMarketAlignment] = useState<Record<string, number>>({});
const [marketAlignmentLoaded, setMarketAlignmentLoaded] = useState(false);
const [interpretationNotice, setInterpretationNotice] = useState<string | null>(null);
const [newJobsCount, setNewJobsCount] = useState<number | null>(null);
const [jobListScrollTop, setJobListScrollTop] = useState(0);
const [scrollRestoreKey] = useState(0);
const [searchDraft, setSearchDraft] = useState("");
const isEditingTopSearchRef = useRef(false);
const [activeRole, setActiveRole] = useState<string | null>(null);
const pendingAutoSelectRoleRef = useRef<string | null>(null);
type SkippedEntry = { job: any; index: number };
const [skippedHistory, setSkippedHistory] = useState<SkippedEntry[]>([]);
const skippedHistoryRef = useRef<SkippedEntry[]>([]);

const roleCategory = (searchParams.get("role") ?? "").trim().toLowerCase();
const searchQuery = (searchParams.get("q") ?? "").trim();
const locationFilter = (searchParams.get("location") ?? "").trim();
const experienceFilter = (searchParams.get("experience") ?? "").trim();
const companyFilter = (searchParams.get("company") ?? "").trim();
const signalsFilter = (searchParams.get("signals") ?? "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
const aiOnlyFilter = searchParams.get("aiOnly") === "1";
const page = Math.max(1, Number(searchParams.get("page") || "1"));
const selectedJobId = (searchParams.get("selected") ?? "").trim();

const filters = {
  location: locationFilter,
  role: searchQuery,
  experience: experienceFilter,
  company: companyFilter,
  signals: signalsFilter,
  aiOnly: aiOnlyFilter,
};
const activeSignalFilter = roleCategory ? [roleCategory] : [];
const roleOptions = (Object.keys(marketAlignment).length > 0
  ? Object.keys(marketAlignment)
  : ["ai", "backend", "platform", "data"]
).sort();
const apiBase = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const apiUrl = (path: string) => `${apiBase}${path}`;

useEffect(() => {
  if (isEditingTopSearchRef.current) return;
  setSearchDraft(searchQuery);
}, [searchQuery]);

useEffect(() => {
  const fetchNewJobsCount = async () => {
    try {
      const res = await fetch(apiUrl("/api/new-jobs-count"));
      const data = await res.json();
      setNewJobsCount(typeof data?.new_jobs === "number" ? data.new_jobs : 0);
    } catch (err) {
      console.error("Failed to load new jobs count:", err);
      setNewJobsCount(0);
    }
  };

  fetchNewJobsCount();
}, []);

useEffect(() => {
  const fetchJobs = async () => {
    try {
      let res;
      if (viewMode === "feed") {
        const params = new URLSearchParams();
        if (filters.location.trim()) params.set("location", filters.location.trim());
        if (filters.role.trim()) params.set("role", filters.role.trim());
        if (filters.experience.trim()) params.set("experience", filters.experience.trim());
        if (filters.company.trim()) params.set("company", filters.company.trim());
        if (activeSignalFilter.length > 0) {
          params.set("signal", activeSignalFilter[0]);
        }
        params.set("page", String(page));
        params.set("page_size", String(pageSize));
        const query = params.toString();

        res = await fetch(apiUrl(`/api/discovery-feed${query ? `?${query}` : ""}`));
      } else {
        res = await fetch(apiUrl("/api/saved-jobs"));
      }

      if (!res.ok) {
        console.error("Discovery API returned non-OK response", res.status);
        setAvailableJobs([]);
        setTotalJobs(0);
        return;
      }

      const data = await res.json();
      if (!data) {
        console.error("Discovery API returned null");
        setAvailableJobs([]);
        setTotalJobs(0);
        return;
      }

      const rawJobs = Array.isArray(data.jobs) ? data.jobs : [];
      setTotalJobs(viewMode === "feed" ? (data.total_jobs ?? 0) : rawJobs.length);

      const jobs = rawJobs.map((j: any) => ({
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
      setAvailableJobs([]);
      setTotalJobs(0);
    }
  };

  fetchJobs();
}, [
  viewMode,
  searchQuery,
  locationFilter,
  experienceFilter,
  companyFilter,
  aiOnlyFilter,
  roleCategory,
  searchParams.get("signals"),
  page,
  pageSize,
]);

useEffect(() => {
  const fetchMarketAlignment = async () => {
    try {
      const res = await fetch(apiUrl("/api/market-alignment"));
      const data = await res.json();
      setMarketAlignment(
        data?.alignment && typeof data.alignment === "object" ? data.alignment : {}
      );
    } catch (err) {
      console.error("Failed to load market alignment:", err);
      setMarketAlignment({});
    } finally {
      setMarketAlignmentLoaded(true);
    }
  };

  fetchMarketAlignment();
}, [
  viewMode,
  searchQuery,
  locationFilter,
  experienceFilter,
  companyFilter,
  aiOnlyFilter,
  roleCategory,
  searchParams.get("signals"),
  page,
]);

useEffect(() => {
  if (view !== "raw") return;
  const container = jobDescriptionRef.current;
  if (!container) return;

  const links = container.querySelectorAll<HTMLAnchorElement>("a[href]");
  links.forEach((link) => {
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener noreferrer");
  });
}, [hydratedContent, view]);

const pipelineJobs = PIPELINE_STATES.reduce((acc: Record<string, any[]>, state) => {
  acc[state] = availableJobs.filter((job) => job.state === state);
  return acc;
}, {});
const visibleJobs = availableJobs.filter((job) => {
  const matchesDomain =
    filters.signals.length === 0 ||
    filters.signals.some((domain) => (job.signals ?? []).includes(domain));
  const matchesSignals =
    activeSignalFilter.length === 0 ||
    activeSignalFilter.some((signal) => (job.signals ?? []).includes(signal));
  const matchesAi = !filters.aiOnly || isLikelyAiRole(job.title);

  return matchesDomain && matchesSignals && matchesAi;
});
const displayedJobs = viewMode === "feed" ? visibleJobs : availableJobs;
const locallyFilteredJobs = activeRole
  ? displayedJobs.filter((job: any) => {
      const roleCategoryValue = String(job?.role_category ?? "").toLowerCase();
      const signals = Array.isArray(job?.signals)
        ? job.signals.map((s: string) => String(s).toLowerCase())
        : [];
      const normalizedActiveRole = activeRole.toLowerCase();
      return roleCategoryValue === normalizedActiveRole || signals.includes(normalizedActiveRole);
    })
  : displayedJobs;
const selectedJob =
  displayedJobs.find((job) => job.id === selectedJobId) ??
  availableJobs.find((job) => job.id === selectedJobId) ??
  null;

const setPage: React.Dispatch<React.SetStateAction<number>> = (value) => {
  const nextPage = Math.max(1, typeof value === "function" ? value(page) : value);
  updateUrlParams((params) => {
    params.set("page", String(nextPage));
  });
};

const updateUrlParams = (mutate: (params: URLSearchParams) => void) => {
  const next = new URLSearchParams(searchParams);
  mutate(next);
  setSearchParams(next);
};

const setSelectedJobParam = (jobId: string | null) => {
  updateUrlParams((params) => {
    if (jobId) {
      params.set("selected", jobId);
    } else {
      params.delete("selected");
    }
  });
};

const pushSkippedHistory = (entry: SkippedEntry) => {
  const next = [...skippedHistoryRef.current, entry];
  skippedHistoryRef.current = next;
  setSkippedHistory(next);
};

const popSkippedHistory = (): SkippedEntry | null => {
  const current = skippedHistoryRef.current;
  if (current.length === 0) return null;
  const entry = current[current.length - 1];
  const next = current.slice(0, -1);
  skippedHistoryRef.current = next;
  setSkippedHistory(next);
  return entry;
};

const handleSelectRoleCategory = (signal: string) => {
  updateUrlParams((params) => {
    params.set("role", signal.toLowerCase());
    params.set("page", "1");
    params.delete("selected");
  });
  setViewMode("feed");
};

const updateFilters = (
  updater:
    | Partial<typeof filters>
    | ((prev: typeof filters) => Partial<typeof filters> | typeof filters)
) => {
  const patch = typeof updater === "function" ? updater(filters) : updater;
  const nextFilters = { ...filters, ...patch };
  updateUrlParams((params) => {
    if (nextFilters.location.length > 0) params.set("location", nextFilters.location);
    else params.delete("location");

    if (nextFilters.role.length > 0) params.set("q", nextFilters.role);
    else params.delete("q");

    if (nextFilters.experience.length > 0) params.set("experience", nextFilters.experience);
    else params.delete("experience");

    if (nextFilters.company.length > 0) params.set("company", nextFilters.company);
    else params.delete("company");

    if (nextFilters.signals.length > 0) params.set("signals", nextFilters.signals.join(","));
    else params.delete("signals");

    if (nextFilters.aiOnly) params.set("aiOnly", "1");
    else params.delete("aiOnly");

    params.set("page", "1");
    params.delete("selected");
  });
};

const performSearch = () => {
  updateFilters({ role: searchDraft.trim() });
  setViewMode("feed");
};

 // --- Handlers ---
 const handleJobSelect = (job: any) => {
  const cachedHydration = hydrationCache.current[job.id];
  phase6Ref.current?.reset();
  setSelectedJobParam(job.id);
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
  setInterpretationNotice(null);
  setUserPreviewUrl(null);
};

 const handleUpdateJobState = async (jobId: string, newState: string) => {
  try {
    const response = await fetch(
      apiUrl("/api/job-state"),
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

    if (
      selectedJobId === jobId &&
      viewMode === "saved" &&
      !SAVED_STATES.includes(newState)
    ) {
      setSelectedJobParam(null);
    }
  } catch (error) {
    console.error("Failed to update job state:", error);
  }
};

 const handleSaveJob = async (jobId: string, currentState?: string | null) => {
  const targetState = currentState === "saved" ? "archived" : "saved";
  await handleUpdateJobState(jobId, targetState);
};

const handleIgnoreJob = async (jobId: string) => {
  const navigableJobs = viewMode === "feed" ? visibleJobs : availableJobs;
  const currentIndex = navigableJobs.findIndex((job) => job.id === jobId);
  const nextJob =
    (currentIndex >= 0 ? navigableJobs[currentIndex + 1] : null) ??
    (currentIndex >= 0 ? navigableJobs[currentIndex - 1] : null) ??
    null;
  const sourceIndex = availableJobs.findIndex((job) => job.id === jobId);
  const skippedJob = sourceIndex >= 0 ? availableJobs[sourceIndex] : null;

  try {
    const response = await fetch(apiUrl("/api/job-ignore"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: jobId }),
    });

    if (!response.ok) {
      let detail = "";
      try {
        const err = await response.json();
        detail = err?.detail ?? "";
      } catch {
        detail = "";
      }
      console.error("Failed to ignore job", detail || response.status);
      return;
    }

    if (skippedJob) {
      pushSkippedHistory({ job: skippedJob, index: sourceIndex });
    }

    setAvailableJobs((prev) => prev.filter((job) => job.id !== jobId));
    setTotalJobs((prev) => Math.max(0, prev - 1));
    if (selectedJobId === jobId) {
      setSelectedJobParam(nextJob?.id ?? null);
    }
  } catch (error) {
    console.error("Failed to ignore job:", error);
  }
};

const handleUndoSkip = async () => {
  const entry = popSkippedHistory();
  if (!entry) return;

  try {
    const response = await fetch(
      apiUrl(`/api/job-state?job_id=${encodeURIComponent(entry.job.id)}`),
      { method: "DELETE" }
    );

    if (!response.ok) {
      pushSkippedHistory(entry);
      return;
    }

    setAvailableJobs((prev) => {
      if (prev.some((job) => job.id === entry.job.id)) {
        return prev;
      }
      const next = [...prev];
      const insertAt = Math.max(0, Math.min(entry.index, next.length));
      next.splice(insertAt, 0, entry.job);
      return next;
    });
    setTotalJobs((prev) => prev + 1);
    setSelectedJobParam(entry.job.id);
  } catch (error) {
    pushSkippedHistory(entry);
    console.error("Failed to undo skipped job:", error);
  }
};

useEffect(() => {
  const onKeyDown = (event: KeyboardEvent) => {
    if (!selectedJob) return;
    if (event.metaKey || event.ctrlKey || event.altKey) return;

    const target = event.target as HTMLElement | null;
    const tag = target?.tagName;
    const isEditable =
      tag === "INPUT" ||
      tag === "TEXTAREA" ||
      tag === "SELECT" ||
      !!target?.isContentEditable;
    if (isEditable) {
      return;
    }

    const key = event.key.toLowerCase();
    if (!["j", "s", "k", "o", "a"].includes(key)) return;

    if (key === "s") {
      event.preventDefault();
      handleSaveJob(selectedJob.id, selectedJob.state);
      return;
    }

    if (key === "k" && event.shiftKey) {
      event.preventDefault();
      handleUndoSkip();
      return;
    }

    if (key === "k") {
      event.preventDefault();
      handleIgnoreJob(selectedJob.id);
      return;
    }

    if (key === "o") {
      event.preventDefault();
      if (selectedJob.url) {
        window.open(selectedJob.url, "_blank", "noopener,noreferrer");
      }
      return;
    }

    if (key === "j") {
      const navigableJobs = viewMode === "feed" ? visibleJobs : availableJobs;
      const currentIndex = navigableJobs.findIndex((job) => job.id === selectedJob.id);
      if (currentIndex < 0) return;

      const nextIndex = event.shiftKey ? currentIndex - 1 : currentIndex + 1;
      if (nextIndex < 0 || nextIndex >= navigableJobs.length) return;

      event.preventDefault();
      handleJobSelect(navigableJobs[nextIndex]);
      return;
    }

    if (key === "a") {
      event.preventDefault();
      requestInterpretation(selectedJob.id);
    }
  };

  window.addEventListener("keydown", onKeyDown);
  return () => {
    window.removeEventListener("keydown", onKeyDown);
  };
}, [availableJobs, selectedJob, viewMode, visibleJobs, skippedHistory.length]);

useEffect(() => {
  if (viewMode !== "feed") return;
  if (!pendingAutoSelectRoleRef.current) return;
  if (pendingAutoSelectRoleRef.current !== roleCategory) return;
  if (selectedJobId) return;
  if (visibleJobs.length === 0) return;
  setSelectedJobParam(visibleJobs[0].id);
  pendingAutoSelectRoleRef.current = null;
}, [viewMode, roleCategory, selectedJobId, visibleJobs]);

useEffect(() => {
  if (!selectedJobId) return;
  mainContentRef.current?.scrollTo({
    top: 0,
    behavior: "auto",
  });
}, [selectedJobId]);

useEffect(() => {
  if (!selectedJob) return;
  const jobId = selectedJob.id;

  const loadArtifacts = async () => {
    setLoadingArtifacts(true);
    try {
      if (hydrationCache.current[jobId]) {
        setHydratedContent(hydrationCache.current[jobId]);
        setHydrationIncomplete(looksIncomplete(hydrationCache.current[jobId]));
      }

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

      const hydrationRes = await fetch(
        apiUrl(`/api/hydrated-job?job_id=${encodeURIComponent(jobId)}`)
      );

      const hydrationData = await hydrationRes.json();

      if (hydrationData?.content) {
        setHydratedContent(hydrationData.content);
        const source = String(hydrationData?.content_source ?? "").toLowerCase();
        setHydrationIncomplete(
          source === "discovery" ? false : looksIncomplete(hydrationData.content)
        );
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

    } finally {
      setLoadingArtifacts(false);
    }
  };

  loadArtifacts();

}, [selectedJob]);

  const handleConsentRevoked = async () => {
  const jobId = selectedJob?.id;
  if (jobId) {
    delete interpretationCache.current[jobId];
    delete spanMapCache.current[jobId];
    interpretationRequestInFlight.current = null;
    try {
      await fetch(
        apiUrl(`/api/job-interpretation?job_id=${encodeURIComponent(jobId)}`),
        { method: "DELETE" }
      );
    } catch (error) {
      console.error("Failed to clear persisted interpretation:", error);
    }
  }
  setRequirements([]);
  setInterpretationResult(null);
  setSpanMap({});
  setView("raw");
  setInterpretationNotice(null);
};
 const handleConsentHandoff = async (payload: any) => {
  console.log("Phase 6 Handoff Emitted:", payload);

  const scope = payload?.consent?.scope;

 if (!scope) return;


  if (scope === "interpret_job_posting") {
    const jobId = payload?.job_id || selectedJob?.id;
    if (!jobId) return;
    await requestInterpretation(jobId);
  }
};

 const handleHydration = async (payload: any) => {
  setIsReading(true);
  try {
    const response = await fetch(
      apiUrl("/api/hydrate-job"),
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
      apiUrl("/api/interpret-manual"),
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
    const res = await fetch(apiUrl("/api/interpret-manual"), {
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

 const requestInterpretation = async (jobId: string) => {
  if (interpretationRequestInFlight.current === jobId) {
    return;
  }
  interpretationRequestInFlight.current = jobId;
  console.log("Interpretation requested.");
  setIsInterpreting(true);

  try {
    const res = await fetch(
      apiUrl(`/api/job-interpretation?job_id=${encodeURIComponent(jobId)}`)
    );

    const result = await res.json();
    console.log("Interpretation response:", result);

    if (!res.ok) {
      throw new Error(result?.detail || "Interpretation failed");
    }
    if (result?.status === "validation_failed") {
      const reason = result?.reason ? ` (${result.reason})` : "";
      const message = result?.message || "Interpretation failed validation.";
      setInterpretationResult(null);
      setRequirements([]);
      setSpanMap({});
      setView("raw");
      setInterpretationNotice(`Analysis could not be completed${reason}: ${message}`);
      phase6Ref.current?.reset();
      return;
    }

    const explicit =
      result.interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];

    setInterpretationNotice(null);
    setInterpretationResult(result.interpretation ?? null);
    interpretationCache.current[jobId] = result.interpretation ?? null;
    if (result?.span_map && typeof result.span_map === "object") {
      setSpanMap(result.span_map);
      spanMapCache.current[jobId] = result.span_map;
    }
    setRequirements(explicit);
    setView("structured");

    phase6Ref.current?.completeInterpretation();
  } catch (error) {
    console.error("Interpretation failed:", error);
    phase6Ref.current?.reset();
  } finally {
    interpretationRequestInFlight.current = null;
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
  const looksLikeHtml = /<[^>]+>/.test(content);
  if (looksLikeHtml) {
    return (
      <div style={articleStyle}>
        <div dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    );
  }

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

  const normalized = content.replace(/\s+/g, " ").trim();
  const text = normalized.toLowerCase();

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

  const contentSignals = [
    "responsibilities",
    "requirements",
    "qualifications",
    "about the role",
    "what you'll do",
    "what you will do",
    "experience",
    "skills",
    "preferred",
    "benefits",
    "about us",
    "about the team",
  ];

  const navHits = navSignals.reduce(
    (count, signal) => count + (text.includes(signal) ? 1 : 0),
    0
  );
  const contentHits = contentSignals.reduce(
    (count, signal) => count + (text.includes(signal) ? 1 : 0),
    0
  );
  const bulletLines = (content.match(/(?:^|\n)\s*[-*•]\s+\S+/g) ?? []).length;

  if (normalized.length < 260) return true;
  if (isBlockedHydrationContent(normalized)) return true;

  if (normalized.length >= 600 && (contentHits >= 2 || bulletLines >= 3)) {
    return false;
  }

  if (normalized.length < 500 && contentHits < 2 && bulletLines < 2) {
    return true;
  }

  return navHits >= 4 && contentHits === 0;
}

function formatPostedDate(postedAt?: string | null): string {
  if (!postedAt) {
    return "Unknown date";
  }
  const posted = new Date(postedAt);
  if (Number.isNaN(posted.getTime())) {
    return "Unknown date";
  }
  return posted.toLocaleDateString();
}

function formatRoleLabel(role: string): string {
  if (!role) return "All Roles";
  return role
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function cleanEvidenceText(raw: string): string {
  if (!raw) return "";

  const withoutStyle = raw.replace(/<style[\s\S]*?<\/style>/gi, " ");
  const withoutScript = withoutStyle.replace(/<script[\s\S]*?<\/script>/gi, " ");
  const withoutTags = withoutScript.replace(/<[^>]+>/g, " ");

  if (typeof document !== "undefined") {
    const textarea = document.createElement("textarea");
    textarea.innerHTML = withoutTags;
    return textarea.value.replace(/\s+/g, " ").trim();
  }

  return withoutTags.replace(/\s+/g, " ").trim();
}

const resolveEvidenceTexts = (spanIds: string[] = []): string[] => {
  const seen = new Set<string>();
  const texts: string[] = [];
  for (const id of spanIds) {
    const text = cleanEvidenceText(spanMap[id] ?? "");
    if (!text || seen.has(text)) continue;
    seen.add(text);
    texts.push(text);
  }
  return texts;
};

const formatSignalLabel = (signal: string): string =>
  signal
    .replace(/[_-]+/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());

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
              jobs={displayedJobs}
              selectedJob={selectedJob}
              onSelectJob={handleJobSelect}
              onSaveJob={handleSaveJob}
              roleCategory={roleCategory}
              viewMode={viewMode}
              setViewMode={setViewMode}
              filters={{
                  location: filters.location,
                  role: filters.role,
                  company: filters.company,
                  experience: filters.experience,
                  signals: filters.signals,
                  aiOnly: filters.aiOnly,
              }}
              setFilters={{
                  setLocationFilter: (value: string) => updateFilters({ location: value }),
                  setRoleFilter: (value: string) => updateFilters({ role: value }),
                  setCompanyFilter: (value: string) => updateFilters({ company: value }),
                  setExperienceFilter: (value: string) => updateFilters({ experience: value }),
                  setSignalsFilter: (value: string[]) => updateFilters({ signals: value }),
                  setAiOnly: (value: boolean) => updateFilters({ aiOnly: value }),
              }}
              page={page}
              setPage={setPage}
              totalPages={totalPages}
              initialScrollTop={jobListScrollTop}
              scrollRestoreKey={scrollRestoreKey}
              onScrollPositionChange={setJobListScrollTop}
          />

          {/* 2. Main Content Area (Center) */}
          <main ref={mainContentRef} style={{
              flex: 1,
              backgroundColor: "#fafafa",
              height: "100vh",       // 🔥 fixed viewport height
              overflowY: "auto",     // 🔥 independent scroll
              display: "flex",
              flexDirection: "column"
          }}>
              <div style={{ padding: "40px" }}>
              {viewMode === "saved" ? (
                  <CenterPanelShell
                    title="Saved Jobs Pipeline"
                    subtitle="Drag jobs between columns to move them through your application process."
                  >
                    <SavedJobsBoard
                        jobsByState={pipelineJobs}
                        selectedJob={selectedJob}
                        onSelectJob={handleJobSelect}
                        toggleJobPriority={handleSaveJob}
                        updateUserJobState={handleUpdateJobState}
                        showHeader={false}
                    />
                  </CenterPanelShell>
              ) : !selectedJob ? (
                  <CenterPanelShell
                    title={roleCategory ? `${formatRoleLabel(roleCategory)} Roles` : "Daily Feed"}
                    subtitle={
                      roleCategory
                        ? "Explore currently active jobs in this role track."
                        : "Search and explore roles matching your strengths."
                    }
                    context={
                      !roleCategory && newJobsCount !== null && newJobsCount > 0 ? (
                        <div
                          style={{
                            padding: "10px 12px",
                            borderRadius: "10px",
                            border: "1px solid #bfdbfe",
                            background: "#eff6ff",
                            color: "#1d4ed8",
                            fontWeight: 600,
                            maxWidth: "700px",
                          }}
                        >
                          {newJobsCount} new jobs since your last visit
                        </div>
                      ) : undefined
                    }
                  >
                  <div style={{ color: "#333" }}>
                      {viewMode === "feed" && !!roleCategory && !selectedJobId ? (
                        <MarketJobGrid
                          jobs={displayedJobs}
                          selectedJob={selectedJob}
                          onSelectJob={handleJobSelect}
                          onSaveJob={handleSaveJob}
                        />
                      ) : (
                      <>
                      <h1 style={{ marginBottom: "8px" }}>Find a role</h1>
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          performSearch();
                        }}
                        style={{ marginBottom: "16px", maxWidth: "700px" }}
                      >
                        <div style={{ display: "flex", gap: "10px" }}>
                        <input
                          type="text"
                          value={searchDraft}
                          onChange={(e) => setSearchDraft(e.target.value)}
                          onFocus={() => {
                            isEditingTopSearchRef.current = true;
                          }}
                          onBlur={() => {
                            isEditingTopSearchRef.current = false;
                          }}
                          onKeyDown={(event) => {
                            if (event.key === "Enter") {
                              event.preventDefault();
                              performSearch();
                            }
                          }}
                          placeholder="Search for roles or companies"
                          style={{
                            flex: 1,
                            padding: "12px 14px",
                            borderRadius: "10px",
                            border: "1px solid #d1d5db",
                            background: "#fff",
                            fontSize: "15px",
                          }}
                        />
                        <button
                          type="submit"
                          style={{
                            padding: "12px 16px",
                            borderRadius: "10px",
                            border: "1px solid #d1d5db",
                            background: "#fff",
                            fontWeight: 600,
                            cursor: "pointer",
                          }}
                        >
                          Search
                        </button>
                        </div>
                      </form>
                      <p style={{ color: "#666", marginBottom: "20px" }}>
                        or explore roles matching your strengths
                      </p>
                      {!marketAlignmentLoaded ? (
                        <div style={{ fontSize: "13px", color: "#777" }}>
                          Loading alignment data...
                        </div>
                      ) : Object.keys(marketAlignment).length === 0 ? (
                        <div style={{ fontSize: "13px", color: "#777" }}>
                          No resume signals configured.
                        </div>
                      ) : (
                        <div style={{ display: "grid", gap: "16px", marginTop: "16px", maxWidth: "700px" }}>
                          {(() => {
                            const entries = Object.entries(marketAlignment).sort((a, b) => b[1] - a[1]);
                            const maxCount = entries.reduce((max, [, count]) => Math.max(max, count), 0);

                            return entries.map(([signal, count]) => {
                              const width = maxCount > 0 ? (count / maxCount) * 100 : 0;

                              return (
                                <div
                                  key={signal}
                                  onClick={() =>
                                    setActiveRole(activeRole === signal ? null : signal)
                                  }
                                  style={{
                                    padding: "16px",
                                    border:
                                      activeRole === signal
                                        ? "1px solid #4f7fff"
                                        : "1px solid #e5e7eb",
                                    borderRadius: "10px",
                                    background: activeRole === signal ? "#eef2ff" : "#ffffff",
                                    cursor: "pointer",
                                    transition: "box-shadow 0.15s ease",
                                    boxShadow:
                                      activeRole === signal
                                        ? "0 4px 12px rgba(79,127,255,0.18)"
                                        : "0 1px 2px rgba(0,0,0,0.06)",
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.boxShadow = "0 1px 2px rgba(0,0,0,0.06)";
                                  }}
                                >
                                  <div
                                    style={{
                                      fontSize: "18px",
                                      fontWeight: 600,
                                      color: "#1f2937",
                                      marginBottom: "6px",
                                    }}
                                  >
                                    {formatSignalLabel(signal)}
                                  </div>
                                  <div
                                    style={{
                                      color: "#4b5563",
                                      fontSize: "14px",
                                      marginBottom: "10px",
                                    }}
                                  >
                                    {count} open roles
                                  </div>
                                  <div
                                    style={{
                                      height: "10px",
                                      background: "#eceff3",
                                      borderRadius: "999px",
                                      overflow: "hidden",
                                    }}
                                  >
                                    <div
                                      style={{
                                        height: "100%",
                                        width: `${width}%`,
                                        background: "#4f7fff",
                                        borderRadius: "999px",
                                      }}
                                    />
                                  </div>
                                </div>
                              );
                            });
                          })()}
                        </div>
                      )}
                      {(activeSignalFilter.length > 0 || filters.role.trim().length > 0) && (
                        <div style={{ marginTop: "30px", color: "#555", fontSize: "14px" }}>
                          {visibleJobs.length > 0
                            ? `Select a role from the left list (${visibleJobs.length} shown).`
                            : "No matching roles found."}
                        </div>
                      )}
                      <MarketJobGrid
                        jobs={locallyFilteredJobs}
                        selectedJob={selectedJob}
                        onSelectJob={handleJobSelect}
                        onSaveJob={handleSaveJob}
                      />
                      </>
                      )}
                  </div>
                  </CenterPanelShell>
              ) : (
                  <CenterPanelShell
                    title={selectedJob.title}
                    subtitle={[selectedJob.company, selectedJob.location, `Posted ${formatPostedDate(selectedJob.posted_at)}`]
                      .filter(Boolean)
                      .join(" • ")}
                    actions={(
                      <button
                        onClick={() => setSelectedJobParam(null)}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "999px",
                          border: "1px solid #d1d5db",
                          background: "#fff",
                          color: "#374151",
                          fontSize: "12px",
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                        title="Back to role jobs"
                      >
                        ← {formatRoleLabel(roleCategory)} roles
                      </button>
                    )}
                  >
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
                      {interpretationNotice && (
                        <div
                          style={{
                            marginBottom: "12px",
                            padding: "10px 12px",
                            borderRadius: "8px",
                            border: "1px solid #f5c2c7",
                            background: "#fff1f2",
                            color: "#7f1d1d",
                            fontSize: "13px",
                          }}
                        >
                          {interpretationNotice}
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
                                  src={apiUrl(`/api/user-preview?url=${encodeURIComponent(userPreviewUrl)}&v=${previewVersion}`)}
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
                          <button
                              onClick={() => handleIgnoreJob(selectedJob.id)}
                              style={{
                                  padding: "10px 14px",
                                  borderRadius: "8px",
                                  border: "1px solid #ddd",
                                  color: "#6b7280",
                                  textDecoration: "none",
                                  fontWeight: 600,
                                  background: "#fff",
                                  marginRight: "8px",
                                  cursor: "pointer"
                              }}
                              title="Skip job"
                              aria-label="Skip job"
                          >
                              × Skip
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
                                          ? "Role Snapshot (Disabled)"
                                          : "Role Snapshot"}
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
                                      <div ref={jobDescriptionRef} style={contentBoxStyle}>
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
                                                  <Card title="Role Snapshot">
                                                      <p style={{ margin: 0, color: "#555", fontSize: "14px" }}>
                                                          Structured role analysis derived from grounded evidence spans.
                                                      </p>
                                                  </Card>

                                                  <Card title="Primary Focus">
                                                      <p style={{margin: 0, color: "#333"}}>
                                                          {interpretationResult?.RoleSummary?.summary_text ?? "No role summary provided."}
                                                      </p>
                                                      <EvidenceBlock spanIds={interpretationResult?.RoleSummary?.evidence_span_ids ?? []} />
                                                  </Card>

                                                  <Card title="Key Capabilities">
                                                      {(interpretationResult?.CapabilityEmphasisSignals ?? []).length > 0 ? (
                                                          <div style={{display: "grid", gap: "12px"}}>
                                                              {(interpretationResult?.CapabilityEmphasisSignals ?? []).map((signal: any, i: number) => (
                                                                  <div key={i}>
                                                                      <div style={{fontWeight: 600, color: "#1f2937"}}>{signal.domain_label}</div>
                                                                      <div style={{fontSize: "14px", color: "#444"}}>{signal.description}</div>
                                                                      <EvidenceBlock spanIds={signal.evidence_span_ids ?? []} />
                                                                  </div>
                                                              ))}
                                                          </div>
                                                      ) : (
                                                          <p style={{margin: 0, color: "#666"}}>No capability signals provided.</p>
                                                      )}
                                                  </Card>

                                                  <Card title="Signals">
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

                                                  <Card title="Project Surfaces">
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
                  </CenterPanelShell>
              )}
              </div>
          </main>

          {/* 3. Authority SidePanel (Right) */}
          {viewMode === "feed" && selectedJob && (
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
