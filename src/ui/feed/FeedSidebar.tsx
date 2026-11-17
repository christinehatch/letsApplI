import React from "react";
import { FeedFilters } from "./FeedFilters";
import { JobList } from "./JobList";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  url?: string;
  first_seen_at?: string | null;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
  signals?: string[];
};

type FeedSidebarProps = {
  jobs: Job[];
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
  roleCategory?: string;
  viewMode: "feed" | "saved";
  setViewMode: (mode: "today" | "feed" | "saved" | "profile") => void;
  filters: {
    location: string;
    role: string;
    company: string;
    experience: string;
    signals: string[];
    aiOnly: boolean;
  };
  setFilters: {
    setLocationFilter: (value: string) => void;
    setRoleFilter: (value: string) => void;
    setCompanyFilter: (value: string) => void;
    setExperienceFilter: (value: string) => void;
    setSignalsFilter: (value: string[]) => void;
    setAiOnly: (value: boolean) => void;
  };
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
  initialScrollTop: number;
  scrollRestoreKey: number;
  onScrollPositionChange: (scrollTop: number) => void;
  saveSearchSlot?: React.ReactNode;
};

export function FeedSidebar({
  jobs,
  selectedJob,
  onSelectJob,
  onSaveJob,
  roleCategory,
  viewMode,
  setViewMode,
  filters,
  setFilters,
  page,
  setPage,
  totalPages,
  initialScrollTop,
  scrollRestoreKey,
  onScrollPositionChange,
  saveSearchSlot,
}: FeedSidebarProps) {
  const [sidebarSearch, setSidebarSearch] = React.useState("");
  const [showKeyboardHint, setShowKeyboardHint] = React.useState(false);
  const [filtersOpen, setFiltersOpen] = React.useState(false);
  const filterSummary = [
    filters.role.trim(),
    filters.location.trim(),
    filters.company.trim(),
    filters.experience.trim(),
    filters.aiOnly ? "AI only" : "",
  ]
    .filter(Boolean)
    .join(" · ");
  const ACRONYMS = new Set(["ai", "ml", "ui", "ux", "qa", "sre", "llm", "nlp"]);
  const formatRoleLabel = (role: string): string =>
    role
      .replace(/[_-]+/g, " ")
      .toLowerCase()
      .split(" ")
      .map((w) => (ACRONYMS.has(w) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
      .join(" ");

  const isFeedLanding = viewMode === "feed" && !selectedJob;
  const isFeedSelected = viewMode === "feed" && !!selectedJob;
  const isInboxMode = viewMode === "saved" || isFeedSelected;
  const roleTitle =
    roleCategory && roleCategory.trim().length > 0
      ? `${formatRoleLabel(roleCategory)} roles`
      : "Search";
  const title = isFeedLanding ? "Search" : isFeedSelected ? roleTitle : "Application Inbox";
  const subtitle = isFeedLanding
    ? "Search every role letsA(ppl)I has found"
    : isFeedSelected
      ? "Review jobs in this role track"
      : "Jump between tracked roles";
  const filteredJobs =
    viewMode === "saved"
      ? jobs.filter((job) =>
          `${job.company ?? ""} ${job.title ?? ""}`
            .toLowerCase()
            .includes(sidebarSearch.toLowerCase())
        )
      : jobs;

  React.useEffect(() => {
    try {
      const dismissed = window.localStorage.getItem("letsappli_keyboard_hint_dismissed");
      if (dismissed === "1") {
        setShowKeyboardHint(false);
      }
    } catch {
      // Ignore storage access failures and keep hint visible.
    }
  }, []);

  const dismissKeyboardHint = () => {
    setShowKeyboardHint(false);
    try {
      window.localStorage.setItem("letsappli_keyboard_hint_dismissed", "1");
    } catch {
      // Ignore storage access failures.
    }
  };

  return (
    <aside
      style={{
        width: "320px",
        borderRight: "1px solid #eee",
        backgroundColor: "#fff",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        boxSizing: "border-box",
      }}
    >
      <div style={{ padding: "16px", borderBottom: "1px solid #eee" }}>
        <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
          <button
            onClick={() => setViewMode("today")}
            style={{
              border: "1px solid #ddd",
              background: "#fff",
              borderRadius: "8px",
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Today
          </button>
          <button
            onClick={() => setViewMode("feed")}
            style={{
              border: "1px solid #ddd",
              background: viewMode === "feed" ? "#f0f7ff" : "#fff",
              borderRadius: "8px",
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Search
          </button>
          <button
            onClick={() => setViewMode("saved")}
            style={{
              border: "1px solid #ddd",
              background: viewMode === "saved" ? "#f0f7ff" : "#fff",
              borderRadius: "8px",
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Saved Jobs
          </button>
          <button
            onClick={() => setViewMode("profile")}
            style={{
              border: "1px solid #ddd",
              background: "#fff",
              borderRadius: "8px",
              padding: "8px 10px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Profile
          </button>
        </div>
        <div style={{ fontSize: "18px", fontWeight: 700, color: "#111827", marginBottom: "8px" }}>
          {title}
        </div>
        {!isInboxMode && (
          <div style={{ fontSize: "12px", color: "#6b7280" }}>
            {subtitle}
          </div>
        )}
        {isInboxMode && (
          <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "4px" }}>
            J next · S save · K skip · O open ·{" "}
            <button
              type="button"
              onClick={() => setShowKeyboardHint(!showKeyboardHint)}
              style={{ border: "none", background: "transparent", color: "#185fa5", cursor: "pointer", padding: 0, fontSize: "12px" }}
              aria-expanded={showKeyboardHint}
            >
              {showKeyboardHint ? "fewer keys" : "all keys"}
            </button>
            {showKeyboardHint && (
              <div style={{ marginTop: "6px", lineHeight: 1.7 }}>
                Shift+J previous · Shift+K undo skip · A summarize
              </div>
            )}
          </div>
        )}
        {viewMode === "saved" && (
          <div>
            <input
              value={sidebarSearch}
              onChange={(e) => setSidebarSearch(e.target.value)}
              placeholder="Search jobs or companies"
              style={{
                width: "100%",
                height: "36px",
                border: "1px solid #ddd",
                borderRadius: "6px",
                padding: "0 12px",
                fontSize: "14px",
                boxSizing: "border-box",
              }}
            />
          </div>
        )}
      </div>
      {viewMode === "feed" && isFeedSelected && !filtersOpen && (
        <div style={{ padding: "12px 16px", borderBottom: "1px solid #eee", display: "flex", gap: "8px", alignItems: "center" }}>
          <div style={{ fontSize: "13px", color: "#374151", minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {filterSummary || "All roles"}
          </div>
          <button
            type="button"
            onClick={() => setFiltersOpen(true)}
            style={{ marginLeft: "auto", border: "none", background: "transparent", color: "#185fa5", cursor: "pointer", fontSize: "13px", padding: 0, flexShrink: 0 }}
          >
            Edit
          </button>
        </div>
      )}
      {viewMode === "feed" && (!isFeedSelected || filtersOpen) && (
        <>
          <div style={{ padding: "16px 16px 8px 16px", fontSize: "12px", fontWeight: 600, color: "#6b7280", display: "flex" }}>
            Filters
            {isFeedSelected && (
              <button
                type="button"
                onClick={() => setFiltersOpen(false)}
                style={{ marginLeft: "auto", border: "none", background: "transparent", color: "#185fa5", cursor: "pointer", fontSize: "12px", padding: 0 }}
              >
                Done
              </button>
            )}
          </div>
          <FeedFilters
            filters={filters}
            setFilters={setFilters}
            viewMode={viewMode}
            setViewMode={setViewMode}
            showChrome={false}
            footer={saveSearchSlot}
          />
        </>
      )}
      {isInboxMode && (
        <>
          <JobList
            jobs={filteredJobs}
            selectedJob={selectedJob}
            onSelectJob={onSelectJob}
            onSaveJob={onSaveJob}
            viewMode={viewMode}
            initialScrollTop={initialScrollTop}
            scrollRestoreKey={scrollRestoreKey}
            onScrollPositionChange={onScrollPositionChange}
          />
        </>
      )}
    </aside>
  );
}
