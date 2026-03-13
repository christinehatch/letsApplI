import React from "react";
import { JobCard } from "../feed/JobCard";

interface MarketJobGridProps {
  jobs: any[];
  selectedJob: any | null;
  onSelectJob: (job: any) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
}

export default function MarketJobGrid({
  jobs,
  selectedJob,
  onSelectJob,
  onSaveJob,
}: MarketJobGridProps) {
  return (
    <div
      style={{
        marginTop: "24px",
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: "16px",
        maxHeight: "60vh",
        overflowY: "auto",
      }}
    >
      {jobs.slice(0, 24).map((job) => (
        <JobCard
          key={job.id}
          job={job}
          selected={selectedJob?.id === job.id}
          onClick={() => onSelectJob(job)}
          onSave={() => onSaveJob(job.id, job.state)}
        />
      ))}
    </div>
  );
}
