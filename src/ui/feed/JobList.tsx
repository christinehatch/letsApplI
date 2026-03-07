import React from "react";
import { JobCard } from "./JobCard";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
};

type JobListProps = {
  jobs: Job[];
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
};

export function JobList({ jobs, selectedJob, onSelectJob }: JobListProps) {
  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "0 20px" }}>
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          selected={selectedJob?.id === job.id}
          onClick={() => onSelectJob(job)}
        />
      ))}
    </div>
  );
}
