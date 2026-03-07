import React from "react";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
};

type JobCardProps = {
  job: Job;
  selected: boolean;
  onClick: () => void;
};

export function JobCard({ job, selected, onClick }: JobCardProps) {
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
    </div>
  );
}
