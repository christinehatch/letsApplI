import React from "react";
import { JobCard } from "./JobCard";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  first_seen_at?: string | null;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
  signals?: string[];
};

type JobListProps = {
  jobs: Job[];
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  onSaveJob: (jobId: string, currentState?: string | null) => void;
  viewMode: "feed" | "saved";
  initialScrollTop: number;
  scrollRestoreKey: number;
  onScrollPositionChange: (scrollTop: number) => void;
};

const SIGNAL_WEIGHTS: Record<string, number> = {
  ai: 5,
  machine_learning: 5,
  ml: 5,
  genai: 5,
  llm: 5,
  backend: 3,
  platform: 3,
  data: 3,
  frontend: 1,
  product: 1,
};

function computeSignalScore(signals: string[]): number {
  return signals.reduce((score, signal) => {
    return score + (SIGNAL_WEIGHTS[signal] ?? 0);
  }, 0);
}

function classify_discovery_jobs(jobs: Job[]): {
  new_today_high: Job[];
  new_today_low: Job[];
  skipped: Job[];
} {
  const now = Date.now();

  const grouped = {
    new_today_high: [] as Job[],
    new_today_low: [] as Job[],
    skipped: [] as Job[],
  };

  for (const job of jobs) {
    const state = (job.state ?? "").toLowerCase();
    const sourceTime = job.first_seen_at ?? job.posted_at;
    const timestamp = sourceTime ? new Date(sourceTime).getTime() : NaN;
    const ageHours = Number.isNaN(timestamp) ? null : (now - timestamp) / (1000 * 60 * 60);

    if (state === "ignored" || state === "archived" || (ageHours !== null && ageHours > 48)) {
      grouped.skipped.push(job);
      continue;
    }

    const signals = (job.signals ?? []).map((s) => s.toLowerCase());
    const score = computeSignalScore(signals);

    if (ageHours !== null && ageHours <= 24) {
      if (score >= 3) {
        grouped.new_today_high.push(job);
      } else {
        grouped.new_today_low.push(job);
      }
      continue;
    }

    // Keep uncategorized jobs visible in low-priority section for now.
    grouped.new_today_low.push(job);
  }

  return grouped;
}

export function JobList({
  jobs,
  selectedJob,
  onSelectJob,
  onSaveJob,
  viewMode,
  initialScrollTop,
  scrollRestoreKey,
  onScrollPositionChange,
}: JobListProps) {
  const listRef = React.useRef<HTMLDivElement | null>(null);

  React.useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = initialScrollTop;
  }, [initialScrollTop, scrollRestoreKey]);

  React.useEffect(() => {
    if (!selectedJob?.id || !listRef.current) return;
    const nodes = listRef.current.querySelectorAll<HTMLElement>("[data-job-id]");
    const match = Array.from(nodes).find((node) => node.dataset.jobId === selectedJob.id);
    if (match) {
      match.scrollIntoView({ block: "nearest" });
    }
  }, [selectedJob?.id]);

  const renderJob = (job: Job) => (
    <div key={job.id} data-job-id={job.id}>
      <JobCard
        job={job}
        selected={selectedJob?.id === job.id}
        onClick={() => onSelectJob(job)}
        onSave={() => onSaveJob(job.id, job.state)}
        variant="row"
      />
    </div>
  );

  const grouped = classify_discovery_jobs(jobs);

  return (
    <div
      ref={listRef}
      onScroll={(e) => onScrollPositionChange(e.currentTarget.scrollTop)}
      style={{
        flex: 1,
        overflowY: "auto",
        padding: "12px 16px 16px 16px",
        boxSizing: "border-box",
      }}
    >
      {viewMode !== "feed" && jobs.map(renderJob)}
      {viewMode === "feed" && (
        <>
          {grouped.new_today_high.length > 0 && (
            <section style={{ padding: "0 0 16px 0" }}>
              <h2 style={{ fontSize: "13px", margin: "12px 0", color: "#666" }}>🔥 New Today</h2>
              {grouped.new_today_high.map(renderJob)}
            </section>
          )}
          {grouped.new_today_low.length > 0 && (
            <section style={{ padding: "0 0 16px 0" }}>
              <h2 style={{ fontSize: "13px", margin: "12px 0", color: "#666" }}>🟡 Lower Priority</h2>
              {grouped.new_today_low.map(renderJob)}
            </section>
          )}
          {grouped.skipped.length > 0 && (
            <section style={{ padding: "0 0 16px 0" }}>
              <h2 style={{ fontSize: "13px", margin: "12px 0", color: "#666" }}>🧊 Skipped</h2>
              {grouped.skipped.map(renderJob)}
            </section>
          )}
        </>
      )}
    </div>
  );
}
