import React, { useState } from "react";

/**
 * One job, calmly: header → one action row → Summary | Posting.
 *
 * Analysis stays user-initiated: the Summary tab shows a single
 * "Summarize this role" invitation until the user asks, and "Stop analyzing
 * this role" removes the saved summary (the old consent revoke).
 */

type Job = {
  id: string;
  title: string;
  company: string;
  location?: string;
  url?: string;
  state?: string | null;
  posted_at?: string | null;
  first_seen_at?: string | null;
};

const STATUS_OPTIONS = [
  ["saved", "Saved"],
  ["applied", "Applied"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
  ["archived", "Archived"],
] as const;

function relative(iso?: string | null): string | null {
  if (!iso) return null;
  const t = new Date(iso);
  if (Number.isNaN(t.getTime())) return null;
  const days = Math.floor((Date.now() - t.getTime()) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 14) return `${days} days ago`;
  if (days < 60) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 365) return `${Math.floor(days / 30)} months ago`;
  return "over a year ago";
}

export type JobDetailProps = {
  job: Job;
  backLabel: string;
  onBack: () => void;
  onSave: () => void;
  onSkip: () => void;
  onStatusChange: (state: string) => void;

  // Posting
  postingContent: string | null;
  renderPosting: (content: string) => React.ReactNode;
  postingRef: React.Ref<HTMLDivElement>;
  isReading: boolean;
  postingBlocked: boolean;
  manualText: string;
  setManualText: (v: string) => void;
  onSummarizePasted: () => void;

  // Summary
  view: "raw" | "structured";
  setView: (v: "raw" | "structured") => void;
  interpretation: any | null;
  isInterpreting: boolean;
  notice: string | null;
  onSummarize: () => void;
  onStopAnalyzing: () => void;
  additionalContext: string;
  setAdditionalContext: (v: string) => void;
  onResummarizeWithContext: () => void;
  renderEvidence: (spanIds: string[]) => React.ReactNode;
  footerExtra?: React.ReactNode;
};

export function JobDetail(p: JobDetailProps) {
  const { job, interpretation } = p;
  const [summaryExpanded, setSummaryExpanded] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);

  const seen = job.posted_at ? `posted ${relative(job.posted_at)}` : job.first_seen_at ? `first seen ${relative(job.first_seen_at)}` : null;
  const metaLine = [job.company, job.location, seen].filter(Boolean).join(" · ");
  const isSaved = ["saved", "applied", "interview", "offer"].includes(job.state ?? "");

  const summaryText: string = interpretation?.RoleSummary?.summary_text ?? "";
  const requirements: any[] = interpretation?.RequirementsAnalysis?.explicit_requirements ?? [];
  const capabilities: any[] = interpretation?.CapabilityEmphasisSignals ?? [];
  const projects: any[] = interpretation?.ProjectOpportunitySignals ?? [];

  const summarizeInvite = (
    <div style={invite}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>Want a summary of what this role asks for?</div>
      <div style={{ ...muted, marginBottom: 12 }}>
        letsA(ppl)I reads this posting and lists what it says, in its own words. It doesn't judge fit, and you can
        stop any time.
      </div>
      <button style={btnPrimary} onClick={p.onSummarize} disabled={p.isInterpreting || !p.postingContent}>
        {p.isInterpreting ? "Summarizing…" : "Summarize this role"}
      </button>
      {!p.postingContent && !p.postingBlocked && <span style={{ ...muted, marginLeft: 10 }}>Loading the posting…</span>}
    </div>
  );

  return (
    <div style={{ maxWidth: 760 }}>
      <button style={backBtn} onClick={p.onBack}>← {p.backLabel}</button>

      <div style={{ ...muted, marginTop: 14 }}>{metaLine}</div>
      <h1 style={titleStyle}>{job.title}</h1>

      <div style={actionRow}>
        <button style={isSaved ? btnSaved : btnPrimary} onClick={p.onSave}>
          {isSaved ? "★ Saved" : "☆ Save"}
        </button>
        <button style={btn} onClick={p.onSkip}>Skip</button>
        {isSaved && (
          <select
            aria-label="Status"
            value={job.state ?? "saved"}
            onChange={(e) => p.onStatusChange(e.target.value)}
            style={selectStyle}
          >
            {STATUS_OPTIONS.map(([v, label]) => (
              <option key={v} value={v}>Status: {label}</option>
            ))}
          </select>
        )}
        {job.url && (
          <a href={job.url} target="_blank" rel="noopener noreferrer" style={{ ...btn, marginLeft: "auto", textDecoration: "none" }}>
            Open posting ↗
          </a>
        )}
      </div>

      <div style={tabs} role="tablist">
        <button role="tab" aria-selected={p.view === "structured"} style={tab(p.view === "structured")} onClick={() => p.setView("structured")}>
          Summary
        </button>
        <button role="tab" aria-selected={p.view === "raw"} style={tab(p.view === "raw")} onClick={() => p.setView("raw")}>
          Posting
        </button>
      </div>

      {p.notice && <div style={noticeStyle}>{p.notice}</div>}

      {p.view === "structured" ? (
        interpretation ? (
          <div>
            {summaryText && (
              <p style={{ margin: 0, lineHeight: 1.6 }}>
                {summaryExpanded || summaryText.length <= 320 ? summaryText : `${summaryText.slice(0, 300).trimEnd()}…`}{" "}
                {summaryText.length > 320 && (
                  <button style={linkBtn} onClick={() => setSummaryExpanded(!summaryExpanded)}>
                    {summaryExpanded ? "Less" : "More"}
                  </button>
                )}
              </p>
            )}

            {requirements.length > 0 && (
              <>
                <h3 style={h3}>What they ask for</h3>
                <ul style={list}>
                  {requirements.map((r, i) => (
                    <li key={i} style={li}>
                      {r.requirement_text}
                      {r.modality && <span style={tag}>{r.modality}</span>}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {capabilities.length > 0 && (
              <>
                <h3 style={h3}>What the work centers on</h3>
                <ul style={list}>
                  {capabilities.map((c, i) => (
                    <li key={i} style={li}>
                      <span style={{ fontWeight: 500 }}>{c.domain_label}</span>
                      {c.description && <span style={{ color: "#4b5563" }}>: {c.description}</span>}
                      {p.renderEvidence(c.evidence_span_ids ?? [])}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {projects.length > 0 && (
              <>
                <h3 style={h3}>{projects.length === 1 ? "One way to show it" : "Ways to show it"}</h3>
                <ul style={list}>
                  {projects.map((pr, i) => (
                    <li key={i} style={li}>
                      <span style={{ fontWeight: 500 }}>{pr.capability_surface}</span>
                      {pr.description && <span style={{ color: "#4b5563" }}>: {pr.description}</span>}
                    </li>
                  ))}
                </ul>
              </>
            )}

            <div style={footer}>
              <span>
                Summarized from the posting
                {interpretation?.confidence && ` · confidence ${String(interpretation.confidence).toLowerCase()}`}
              </span>
              <span style={{ display: "flex", gap: 14 }}>
                <button style={linkBtn} onClick={() => setContextOpen(!contextOpen)}>Add context</button>
                <button style={linkBtn} onClick={p.onStopAnalyzing}>Stop analyzing this role</button>
              </span>
            </div>
            {contextOpen && (
              <div style={{ marginTop: 10 }}>
                <textarea
                  value={p.additionalContext}
                  onChange={(e) => p.setAdditionalContext(e.target.value)}
                  placeholder="Anything the posting leaves out, such as notes from a recruiter call"
                  style={textarea}
                />
                <button
                  style={btn}
                  onClick={p.onResummarizeWithContext}
                  disabled={!p.additionalContext.trim() || p.isInterpreting}
                >
                  {p.isInterpreting ? "Summarizing…" : "Summarize again with this context"}
                </button>
              </div>
            )}
            {p.footerExtra}
          </div>
        ) : (
          summarizeInvite
        )
      ) : p.postingBlocked ? (
        <div style={invite}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>This posting couldn't be loaded automatically</div>
          <div style={{ ...muted, marginBottom: 12 }}>
            Some job sites block automated access. Paste the description to read and summarize it here.
          </div>
          <textarea
            value={p.manualText}
            onChange={(e) => p.setManualText(e.target.value)}
            placeholder="Paste the job description"
            style={{ ...textarea, minHeight: 200 }}
          />
          <button style={btn} onClick={p.onSummarizePasted} disabled={!p.manualText.trim() || p.isInterpreting}>
            {p.isInterpreting ? "Summarizing…" : "Summarize pasted posting"}
          </button>
        </div>
      ) : p.postingContent ? (
        <>
          {!interpretation && summarizeInvite}
          <div ref={p.postingRef} style={postingBox}>{p.renderPosting(p.postingContent)}</div>
        </>
      ) : (
        <div style={muted}>{p.isReading ? "Loading the posting…" : "The posting isn't loaded yet."}</div>
      )}
    </div>
  );
}

const muted: React.CSSProperties = { fontSize: 13, color: "#6b7280" };
const titleStyle: React.CSSProperties = { fontSize: 26, fontWeight: 600, lineHeight: 1.25, margin: "4px 0 0", color: "#111827" };
const actionRow: React.CSSProperties = { display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", margin: "18px 0 22px" };
const btn: React.CSSProperties = {
  padding: "8px 14px",
  borderRadius: 9,
  border: "1px solid #d1d5db",
  background: "#fff",
  color: "#1f2937",
  fontSize: 14,
  cursor: "pointer",
  whiteSpace: "nowrap",
  display: "inline-flex",
  alignItems: "center",
};
const btnPrimary: React.CSSProperties = { ...btn, background: "#111827", color: "#fff", borderColor: "#111827" };
const btnSaved: React.CSSProperties = { ...btn, color: "#7a5a00", borderColor: "#e9d6a3", background: "#fffbeb" };
const selectStyle: React.CSSProperties = { ...btn, paddingRight: 8 };
const backBtn: React.CSSProperties = { border: "none", background: "transparent", color: "#6b7280", fontSize: 13, cursor: "pointer", padding: 0 };
const tabs: React.CSSProperties = { display: "flex", gap: 20, borderBottom: "1px solid #e5e7eb", marginBottom: 20 };
const tab = (on: boolean): React.CSSProperties => ({
  border: "none",
  background: "transparent",
  padding: "0 0 8px",
  fontSize: 14,
  cursor: "pointer",
  color: on ? "#111827" : "#6b7280",
  fontWeight: on ? 600 : 400,
  boxShadow: on ? "inset 0 -2px 0 #111827" : "none",
});
const h3: React.CSSProperties = { fontSize: 13, fontWeight: 600, color: "#6b7280", margin: "24px 0 8px" };
const list: React.CSSProperties = { margin: 0, paddingLeft: 18 };
const li: React.CSSProperties = { margin: "6px 0", lineHeight: 1.5 };
const tag: React.CSSProperties = { fontSize: 11.5, color: "#6b7280", border: "1px solid #e5e7eb", borderRadius: 6, padding: "0 6px", marginLeft: 6 };
const footer: React.CSSProperties = {
  marginTop: 28,
  paddingTop: 12,
  borderTop: "1px solid #e5e7eb",
  fontSize: 12.5,
  color: "#9ca3af",
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  flexWrap: "wrap",
};
const linkBtn: React.CSSProperties = { border: "none", background: "transparent", color: "#185fa5", cursor: "pointer", padding: 0, fontSize: "inherit" };
const invite: React.CSSProperties = { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: "18px 20px", marginBottom: 16 };
const noticeStyle: React.CSSProperties = {
  marginBottom: 14,
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #f5c2c7",
  background: "#fff1f2",
  color: "#7f1d1d",
  fontSize: 13,
};
const textarea: React.CSSProperties = {
  width: "100%",
  minHeight: 90,
  padding: 10,
  border: "1px solid #d1d5db",
  borderRadius: 8,
  fontFamily: "inherit",
  fontSize: 14,
  marginBottom: 8,
  boxSizing: "border-box",
};
const postingBox: React.CSSProperties = { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: "20px 24px", lineHeight: 1.6 };
