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
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
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
    aiFilter: string;
  };
  setFilters: {
    setLocationFilter: (value: string) => void;
    setRoleFilter: (value: string) => void;
    setCompanyFilter: (value: string) => void;
    setExperienceFilter: (value: string) => void;
    setAiFilter: (value: string) => void;
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
      <JobList
        jobs={jobs}
        selectedJob={selectedJob}
        onSelectJob={onSelectJob}
        onSaveJob={onSaveJob}
      />
      {viewMode === "feed" && (
        <FeedPagination page={page} setPage={setPage} totalPages={totalPages} />
      )}
    </aside>
  );
}
