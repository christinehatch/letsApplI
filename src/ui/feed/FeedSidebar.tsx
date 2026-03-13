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
  setViewMode: (mode: "feed" | "saved") => void;
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
}: FeedSidebarProps) {
  const [sidebarSearch, setSidebarSearch] = React.useState("");
  const [showKeyboardHint, setShowKeyboardHint] = React.useState(true);
  const formatRoleLabel = (role: string): string =>
    role
      .replace(/[_-]+/g, " ")
      .toLowerCase()
      .replace(/\b\w/g, (c) => c.toUpperCase());

  const isFeedLanding = viewMode === "feed" && !selectedJob;
  const isFeedSelected = viewMode === "feed" && !!selectedJob;
  const isInboxMode = viewMode === "saved" || isFeedSelected;
  const roleTitle =
    roleCategory && roleCategory.trim().length > 0
      ? `${formatRoleLabel(roleCategory)} Roles`
      : "Daily Feed";
  const title = isFeedLanding ? "Daily Feed" : isFeedSelected ? roleTitle : "Application Inbox";
  const subtitle = isFeedLanding
    ? "Discover and triage new roles"
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
            Daily Feed
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
        </div>
        <div style={{ fontSize: "18px", fontWeight: 700, color: "#111827", marginBottom: "8px" }}>
          {title}
        </div>
        <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: isInboxMode ? "16px" : "0" }}>
          {subtitle}
        </div>
        {isInboxMode && showKeyboardHint && (
          <div style={{ marginBottom: "16px" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "8px",
                marginBottom: "8px",
              }}
            >
              <div style={{ fontSize: "12px", fontWeight: 600, color: "#4b5563" }}>
                Keyboard triage
              </div>
              <button
                type="button"
                onClick={dismissKeyboardHint}
                style={{
                  border: "1px solid #e5e7eb",
                  background: "#fff",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "#4b5563",
                  padding: "4px 8px",
                  cursor: "pointer",
                }}
              >
                Got it
              </button>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {[
                "J next",
                "Shift+J prev",
                "S save",
                "K skip",
                "Shift+K unskip",
                "O open",
                "A analyze",
              ].map((shortcut) => (
                <span
                  key={shortcut}
                  style={{
                    fontSize: "12px",
                    color: "#4b5563",
                    border: "1px solid #e5e7eb",
                    background: "#f9fafb",
                    borderRadius: "6px",
                    padding: "4px 8px",
                  }}
                >
                  {shortcut}
                </span>
              ))}
            </div>
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
      {viewMode === "feed" && (
        <>
          <div style={{ padding: "16px 16px 8px 16px", fontSize: "12px", fontWeight: 600, color: "#6b7280" }}>
            Sidebar Filters
          </div>
          <FeedFilters
            filters={filters}
            setFilters={setFilters}
            viewMode={viewMode}
            setViewMode={setViewMode}
            showChrome={false}
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
