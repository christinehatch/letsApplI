import React from "react";
import { JobCard } from "./JobCard";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
};

type JobListProps = {
  jobs: Job[];
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
};

export function JobList({ jobs, selectedJob, onSelectJob, onSaveJob }: JobListProps) {
  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "0 20px" }}>
      {jobs.map((job) => (
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
