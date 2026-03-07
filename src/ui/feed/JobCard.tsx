import React from "react";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  posted_at?: string | null;
  provider?: string;
};

type JobCardProps = {
  job: Job;
  selected: boolean;
  onClick: () => void;
};

function formatProvider(provider?: string): string {
  if (!provider) {
    return "Unknown";
  }
  const normalized = provider.toLowerCase();
  if (normalized === "greenhouse_job_board_api" || normalized === "greenhouse") {
    return "Greenhouse";
  }
  if (normalized === "lever_job_board_api" || normalized === "lever") {
    return "Lever";
  }
  return provider;
}

function formatPostedDate(postedAt?: string | null): string {
  if (!postedAt) {
    return "Unknown date";
  }

  const posted = new Date(postedAt);
  if (Number.isNaN(posted.getTime())) {
    return "Unknown date";
  }

  const now = new Date();
  const diffMs = now.getTime() - posted.getTime();
  if (diffMs < 0) {
    return "Today";
  }

  const dayMs = 24 * 60 * 60 * 1000;
  const days = Math.floor(diffMs / dayMs);

  if (days <= 0) {
    return "Today";
  }
  if (days === 1) {
    return "1 day ago";
  }
  if (days < 14) {
    return `${days} days ago`;
  }

  const weeks = Math.floor(days / 7);
  if (weeks === 1) {
    return "1 week ago";
  }
  return `${weeks} weeks ago`;
}

export function JobCard({ job, selected, onClick }: JobCardProps) {
  const formattedPostedDate = formatPostedDate(job.posted_at);
  const formattedProvider = formatProvider(job.provider);

  return (
    <div
      onClick={onClick}
      style={{
        padding: "16px",
        border: selected ? "2px solid #0070f3" : "1px solid #eee",
        borderRadius: "12px",
        marginBottom: "12px",
        cursor: "pointer",
        backgroundColor: selected ? "#f0f7ff" : "#fff",
      }}
    >
      <div
        style={{
          fontSize: "12px",
          fontWeight: "bold",
          color: "#0070f3",
          marginBottom: "4px",
        }}
      >
        {job.company}
      </div>
      <div style={{ fontWeight: 600, fontSize: "14px" }}>{job.title}</div>
      {job.location && (
        <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>{job.location}</div>
      )}
      <div style={{ fontSize: "12px", color: "#666", marginTop: "6px" }}>
        Posted {formattedPostedDate} • {formattedProvider}
      </div>
    </div>
  );
}
