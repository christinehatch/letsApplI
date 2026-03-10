import React from "react";
import { FeedFilters } from "./FeedFilters";
import { JobList } from "./JobList";
import { FeedPagination } from "./FeedPagination";

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
};

export function FeedSidebar({
  jobs,
  selectedJob,
  onSelectJob,
  onSaveJob,
  viewMode,
  setViewMode,
  filters,
  setFilters,
  page,
  setPage,
  totalPages,
}: FeedSidebarProps) {
  const toggleDomain = (domain: string) => {
    if (filters.signals.includes(domain)) {
      setFilters.setSignalsFilter(filters.signals.filter((d) => d !== domain));
      return;
    }
    setFilters.setSignalsFilter([...filters.signals, domain]);
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
      }}
    >
      <FeedFilters
        filters={filters}
        setFilters={setFilters}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />
      {viewMode === "feed" && filters.signals.length > 0 && (
        <div style={{ padding: "0 20px 10px 20px" }}>
          <div style={{ fontSize: "12px", marginBottom: "6px", color: "#666" }}>
            Active Filters
          </div>
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            {filters.signals.map((domain) => (
              <span
                key={domain}
                style={{
                  padding: "4px 8px",
                  borderRadius: "14px",
                  background: "#f3f3f3",
                  fontSize: "12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                {domain.replace("_", " ").toUpperCase()}
                <button
                  onClick={() => toggleDomain(domain)}
                  style={{
                    border: "none",
                    background: "none",
                    cursor: "pointer",
                    fontWeight: "bold",
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
      <JobList
        jobs={jobs}
        selectedJob={selectedJob}
        onSelectJob={onSelectJob}
        onSaveJob={onSaveJob}
        viewMode={viewMode}
      />
      {viewMode === "feed" && (
        <FeedPagination page={page} setPage={setPage} totalPages={totalPages} />
      )}
    </aside>
  );
}
