import React from "react";
import { JobCard } from "./JobCard";

/**
 * The Search page body. Jobs come first: a one-line count, a compact row of
 * areas to narrow by, then the roles themselves (newest first), then paging.
 * Filters live in the sidebar; this view doesn't repeat them.
 */
export function SearchResults({
  jobs,
  totalJobs,
  page,
  pageSize,
  totalPages,
  onPage,
  location,
  keyword,
  area,
  areas,
  areasLoaded,
  areaLabel,
  onSelectArea,
  onClearArea,
  newSinceLastVisit,
  selectedJobId,
  onSelectJob,
  onSaveJob,
}: {
  jobs: any[];
  totalJobs: number;
  page: number;
  pageSize: number;
  totalPages: number;
  onPage: (page: number) => void;
  location: string;
  keyword: string;
  area: string | null;
  areas: Record<string, number>;
  areasLoaded: boolean;
  areaLabel: (signal: string) => string;
  onSelectArea: (signal: string) => void;
  onClearArea: () => void;
  newSinceLastVisit: number | null;
  selectedJobId: string | null;
  onSelectJob: (job: any) => void;
  onSaveJob: (jobId: string, state?: string | null) => void;
}) {
  const noun = totalJobs === 1 ? "role" : "roles";
  const headline = [
    `${totalJobs.toLocaleString()} open`,
    area ? `${areaLabel(area)} ${noun}` : noun,
    location ? `in ${location}` : null,
    keyword ? `matching “${keyword}”` : null,
  ]
    .filter(Boolean)
    .join(" ");

  const areaEntries = Object.entries(areas)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1]);

  const first = totalJobs === 0 ? 0 : (page - 1) * pageSize + 1;
  const last = Math.min(page * pageSize, totalJobs);

  return (
    <div style={{ maxWidth: 760 }}>
      <h1 style={{ margin: 0, fontSize: 22, fontWeight: 600, color: "#111827" }}>{headline}</h1>
      <div style={{ marginTop: 4, fontSize: 13, color: "#6b7280" }}>
        {totalJobs > 0 ? "Newest first" : ""}
        {totalJobs > 0 && newSinceLastVisit ? ` · ${newSinceLastVisit.toLocaleString()} new since your last visit` : ""}
      </div>

      {areasLoaded && areaEntries.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 14 }} aria-label="Narrow by area">
          <Chip active={!area} onClick={onClearArea}>All</Chip>
          {areaEntries.map(([signal, count]) => (
            <Chip
              key={signal}
              active={area === signal}
              onClick={() => (area === signal ? onClearArea() : onSelectArea(signal))}
            >
              {areaLabel(signal)} <span style={{ opacity: 0.6 }}>{count.toLocaleString()}</span>
            </Chip>
          ))}
        </div>
      )}

      <div style={{ marginTop: 18 }}>
        {jobs.length === 0 ? (
          <div style={{ padding: "28px 0", color: "#4b5563", fontSize: 14, lineHeight: 1.5 }}>
            No open roles match.
            <span style={{ display: "block", color: "#6b7280" }}>
              Try fewer words, a different spelling, or clearing the location.
            </span>
          </div>
        ) : (
          jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              variant="row"
              selected={selectedJobId === job.id}
              onClick={() => onSelectJob(job)}
              onSave={() => onSaveJob(job.id, job.state)}
            />
          ))
        )}
      </div>

      {totalPages > 1 && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, margin: "8px 0 24px", fontSize: 13, color: "#6b7280" }}>
          <span>
            {first.toLocaleString()}–{last.toLocaleString()} of {totalJobs.toLocaleString()}
          </span>
          <span style={{ flex: 1 }} />
          <button type="button" style={pagerBtn} disabled={page <= 1} onClick={() => onPage(page - 1)}>
            ← Newer
          </button>
          <button type="button" style={pagerBtn} disabled={page >= totalPages} onClick={() => onPage(page + 1)}>
            Older →
          </button>
        </div>
      )}
    </div>
  );
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      style={{
        padding: "5px 11px",
        borderRadius: 999,
        border: `1px solid ${active ? "#111827" : "#d1d5db"}`,
        background: active ? "#111827" : "#fff",
        color: active ? "#fff" : "#374151",
        fontSize: 13,
        fontWeight: 500,
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}

const pagerBtn: React.CSSProperties = {
  padding: "6px 12px",
  borderRadius: 8,
  border: "1px solid #d1d5db",
  background: "#fff",
  color: "#374151",
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
