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
};

type FeedSidebarProps = {
  jobs: Job[];
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  filters: {
    location: string;
    role: string;
    company: string;
    experience: string;
  };
  setFilters: {
    setLocationFilter: (value: string) => void;
    setRoleFilter: (value: string) => void;
    setCompanyFilter: (value: string) => void;
    setExperienceFilter: (value: string) => void;
  };
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
};

export function FeedSidebar({
  jobs,
  selectedJob,
  onSelectJob,
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
      <FeedFilters filters={filters} setFilters={setFilters} />
      <JobList jobs={jobs} selectedJob={selectedJob} onSelectJob={onSelectJob} />
      <FeedPagination page={page} setPage={setPage} totalPages={totalPages} />
    </aside>
  );
}
