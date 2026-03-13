import React, { memo } from "react";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
};

type JobCardProps = {
  job: Job;
  selected: boolean;
  onClick: () => void;
  onSave: () => void;
  onSkip?: () => void;
  onStatusChange?: (newStatus: string) => void;
  isDragging?: boolean;
  variant?: "default" | "row" | "board";
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

function formatStateLabel(state?: string | null): string | null {
  if (!state) {
    return null;
  }
  if (state === "saved") {
    return "Saved";
  }
  if (state === "applied") {
    return "Applied";
  }
  if (state === "interview") {
    return "Interview";
  }
  if (state === "offer") {
    return "Offer";
  }
  if (state === "rejected") {
    return "Rejected";
  }
  if (state === "archived") {
    return "Archived";
  }
  if (state === "ignored") {
    return "Ignored";
  }
  return state;
}

function stateBadgeColor(state?: string | null): string {
  if (state === "saved") return "#666";
  if (state === "applied") return "#1f6feb";
  if (state === "interview") return "#8250df";
  if (state === "offer") return "#1a7f37";
  if (state === "rejected") return "#cf222e";
  if (state === "archived") return "#8c959f";
  if (state === "ignored") return "#8c959f";
  return "#666";
}

export const JobCard = memo(function JobCard({
  job,
  selected,
  onClick,
  onSave,
  onSkip,
  onStatusChange,
  isDragging = false,
  variant = "default",
}: JobCardProps) {
  const [isHovered, setIsHovered] = React.useState(false);
  const SAVED_STATES = ["saved", "applied", "interview", "offer"];
  const formattedPostedDate = formatPostedDate(job.posted_at);
  const formattedProvider = formatProvider(job.provider);
  const stateLabel = formatStateLabel(job.state);
  const isSaved = SAVED_STATES.includes(job.state ?? "");
  const showAiBadge = isLikelyAiRole(job.title);
  const isRow = variant === "row";
  const isBoard = variant === "board";

  const cardStyle: React.CSSProperties = {
    padding: isRow ? "12px" : "14px",
    borderRadius: isRow ? "8px" : "10px",
    marginBottom: isRow ? "10px" : isBoard ? "0" : "12px",
    border: isRow ? "1px solid #e5e7eb" : selected ? "1px solid #cddcff" : "1px solid transparent",
    background: isRow
      ? selected
        ? "#eef3ff"
        : isHovered
          ? "#f8fafc"
          : "#fff"
      : selected
        ? "#eef3ff"
        : "#fff",
    cursor: "pointer",
    opacity: isDragging ? 0.9 : 1,
    transform: isDragging ? "scale(1.02)" : !isRow && isHovered ? "translateY(-1px)" : "none",
    boxShadow: isDragging
      ? "0 10px 25px rgba(0,0,0,0.2)"
      : !isRow && isHovered
        ? "0 2px 4px rgba(0,0,0,0.08)"
        : !isRow
          ? "0 1px 2px rgba(0,0,0,0.05)"
          : "none",
    transition: "background-color 120ms ease, box-shadow 120ms ease, transform 120ms ease",
    width: "100%",
    boxSizing: "border-box",
  };

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={cardStyle}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "8px",
        }}
      >
        <div style={{ minWidth: 0 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "4px",
            }}
          >
            <div
              style={{
                fontSize: "13px",
                fontWeight: 600,
                color: "#2b6cb0",
              }}
            >
              {job.company}
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSave();
              }}
              style={{
                fontSize: "14px",
                cursor: "pointer",
                border: "none",
                background: "transparent",
                color: isSaved ? "#f5b400" : "#bbb",
                borderRadius: "4px",
                padding: 0,
                lineHeight: 1,
              }}
              aria-label={isSaved ? "Saved" : "Save"}
              title={isSaved ? "Saved" : "Save"}
            >
              {isSaved ? "★" : "☆"}
            </button>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <div
              style={{
                fontWeight: 600,
                fontSize: "15px",
                color: "#111",
                wordBreak: "break-word",
                lineHeight: 1.3,
              }}
            >
              {job.title}
            </div>
            {showAiBadge && (
              <span
                style={{
                  fontSize: "11px",
                  background: "#eef2ff",
                  color: "#4338ca",
                  padding: "2px 6px",
                  borderRadius: "6px",
                }}
              >
                🧠 AI
              </span>
            )}
          </div>
        </div>
        {onSkip && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSkip();
            }}
            style={{
              fontSize: "18px",
              cursor: "pointer",
              border: "none",
              background: "transparent",
              color: "#9ca3af",
              borderRadius: "6px",
              padding: 0,
              lineHeight: 1,
            }}
            aria-label="Skip"
            title="Skip"
          >
            ×
          </button>
        )}
      </div>
      {job.location && (
        <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>{job.location}</div>
      )}
      <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
        Posted {formattedPostedDate} • {formattedProvider}
      </div>
      {stateLabel && (
        <div
          style={{
            marginTop: "8px",
            fontSize: "12px",
            color: stateBadgeColor(job.state),
            fontWeight: 500,
          }}
        >
          {stateLabel}
        </div>
      )}
      {onStatusChange && (
        <div style={{ marginTop: "8px" }}>
          <select
            value={job.state ?? "saved"}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              e.stopPropagation();
              onStatusChange(e.target.value);
            }}
            style={{
              width: "100%",
              padding: "8px 10px",
              border: "1px solid #ddd",
              borderRadius: "6px",
              fontSize: "12px",
              background: "#fff",
            }}
          >
            <option value="saved">Saved</option>
            <option value="applied">Applied</option>
            <option value="interview">Interview</option>
            <option value="offer">Offer</option>
            <option value="rejected">Rejected</option>
            <option value="ignored">Ignored</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      )}
    </div>
  );
});

export function isLikelyAiRole(title: string): boolean {
  const terms = [
    "ai",
    "machine learning",
    "ml",
    "genai",
    "llm",
    "artificial intelligence",
  ];

  const lower = title.toLowerCase();
  return terms.some((term) => lower.includes(term));
}
