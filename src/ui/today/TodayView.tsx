import React, { useCallback, useEffect, useMemo, useState } from "react";

/**
 * Today: saved searches → a short, finite set of new roles, one at a time →
 * "You're caught up".
 *
 * - Roles leave Today only by an explicit decision: Save, Skip, or Later.
 * - Nothing runs in the background; "Check for new roles" is a button.
 * - No ranking by fit. Order is: searches take turns, newest first.
 */

type SavedSearch = {
  id: number;
  name: string;
  role: string;
  location: string;
  company: string;
  open_count: number;
  new_count: number;
  top_companies: string[];
  company_count: number;
};

type TodayItem = {
  job_id: string;
  job_ids: string[];
  company: string;
  title: string;
  locations: string[];
  url: string;
  first_seen_at: string | null;
  signals: string[];
  source: { type: "search" | "later"; name: string; search_id?: number };
};

type TodayResponse = {
  items: TodayItem[];
  new_total: number;
  new_shown: number;
  later_count: number;
};

type Decision = "saved" | "ignored" | "later";
type Stage = "home" | "focus" | "done";

const LAST_CHECKED_KEY = "letsappli_last_checked_at";

const SIGNAL_LABELS: Record<string, string> = {
  ai_ml: "AI / ML",
  ai: "AI",
  ml: "ML",
  data: "Data",
  backend: "Backend",
  frontend: "Frontend",
  fullstack: "Full stack",
  platform: "Platform",
  infra: "Infrastructure",
  security: "Security",
  product: "Product",
  design: "Design",
  mobile: "Mobile",
  staff: "Staff",
  senior: "Senior",
  principal: "Principal",
  manager: "Manager",
  junior: "Junior",
};

function signalLabel(signal: string): string {
  return (
    SIGNAL_LABELS[signal.toLowerCase()] ??
    signal.replace(/[_-]+/g, " ").replace(/^\w/, (c) => c.toUpperCase())
  );
}

function relativeTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "";
  const days = Math.floor((Date.now() - then.getTime()) / 86_400_000);
  if (days <= 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 14) return "1 week ago";
  if (days < 60) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 365) return `${Math.floor(days / 30)} months ago`;
  return "over a year ago";
}

function readLastChecked(): string | null {
  try {
    return window.localStorage.getItem(LAST_CHECKED_KEY);
  } catch {
    return null;
  }
}

function writeLastChecked(iso: string) {
  try {
    window.localStorage.setItem(LAST_CHECKED_KEY, iso);
  } catch {
    // Storage can be unavailable; the label just won't persist.
  }
}

export function TodayView({
  apiUrl,
  onOpenSearch,
  onOpenSaved,
  onOpenInApp,
}: {
  apiUrl: (path: string) => string;
  onOpenSearch: () => void;
  onOpenSaved: () => void;
  onOpenInApp: (job: { job_id: string; company: string; title: string }) => void;
}) {
  const [stage, setStage] = useState<Stage>("home");
  const [searches, setSearches] = useState<SavedSearch[] | null>(null);
  const [today, setToday] = useState<TodayResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(readLastChecked());
  const [index, setIndex] = useState(0);
  const [deciding, setDeciding] = useState(false);
  const [tally, setTally] = useState<Record<Decision, number>>({ saved: 0, ignored: 0, later: 0 });

  const load = useCallback(async () => {
    setError(null);
    try {
      const [s, t] = await Promise.all([
        fetch(apiUrl("/api/saved-searches")).then((r) => r.json()),
        fetch(apiUrl("/api/today")).then((r) => r.json()),
      ]);
      setSearches(s?.searches ?? []);
      setToday(t ?? null);
    } catch {
      setError("Couldn't reach the letsA(ppl)I server.");
    }
  }, [apiUrl]);

  useEffect(() => {
    load();
  }, [load]);

  const items = today?.items ?? [];
  const current = stage === "focus" ? items[index] : undefined;

  const start = () => {
    setIndex(0);
    setTally({ saved: 0, ignored: 0, later: 0 });
    setStage(items.length > 0 ? "focus" : "done");
  };

  const leaveFocus = useCallback(() => {
    setStage("home");
    load();
  }, [load]);

  const decide = useCallback(
    async (decision: Decision) => {
      if (!current || deciding) return;
      setDeciding(true);
      setError(null);
      try {
        const res = await fetch(apiUrl("/api/today/decide"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_ids: current.job_ids, decision }),
        });
        if (!res.ok) throw new Error();
        setTally((t) => ({ ...t, [decision]: t[decision] + 1 }));
        if (index + 1 >= items.length) {
          setStage("done");
        } else {
          setIndex(index + 1);
        }
      } catch {
        setError("That didn't save. Try again.");
      } finally {
        setDeciding(false);
      }
    },
    [apiUrl, current, deciding, index, items.length]
  );

  const openPosting = useCallback(() => {
    if (current?.url) window.open(current.url, "_blank", "noopener,noreferrer");
  }, [current]);

  useEffect(() => {
    if (stage !== "focus") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
      const key = e.key.toLowerCase();
      if (key === "s") { e.preventDefault(); decide("saved"); }
      else if (key === "k") { e.preventDefault(); decide("ignored"); }
      else if (key === "l") { e.preventDefault(); decide("later"); }
      else if (key === "o") { e.preventDefault(); openPosting(); }
      else if (e.key === "Escape") { e.preventDefault(); leaveFocus(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [stage, decide, openPosting, leaveFocus]);

  const checkForNewRoles = async () => {
    setChecking(true);
    setCheckResult(null);
    setError(null);
    try {
      const res = await fetch(apiUrl("/api/discovery/refresh"), { method: "POST" });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Check failed.");
      const now = new Date().toISOString();
      writeLastChecked(now);
      setLastChecked(now);
      setCheckResult(
        data.new_roles > 0
          ? `Found ${data.new_roles} new postings across all companies.`
          : "No new postings since the last check."
      );
      await load();
    } catch (e) {
      setError(e instanceof Error && e.message ? e.message : "Couldn't check for new roles.");
    } finally {
      setChecking(false);
    }
  };

  const removeSearch = async (id: number) => {
    await fetch(apiUrl(`/api/saved-searches/${id}`), { method: "DELETE" }).catch(() => null);
    load();
  };

  const newShown = today?.new_shown ?? 0;
  const newTotal = today?.new_total ?? 0;
  const laterCount = today?.later_count ?? 0;
  const startLabel = useMemo(() => {
    if (items.length === 0) return null;
    return `Start today's ${items.length}`;
  }, [items.length]);

  return (
    <div style={page}>
      <nav style={topBar}>
        <span style={{ ...tab, ...tabActive }}>Today</span>
        <button style={tab} onClick={onOpenSearch}>Search</button>
        <button style={tab} onClick={onOpenSaved}>Saved jobs</button>
      </nav>

      <div style={column}>
        {error && <p style={errorText}>{error}</p>}

        {stage === "home" && (
          <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 16, flexWrap: "wrap" }}>
              <div>
                <h1 style={h1}>
                  {searches === null
                    ? "Loading…"
                    : searches.length === 0
                      ? "Build your Today"
                      : newShown > 0
                        ? `${newTotal} new ${newTotal === 1 ? "role" : "roles"} across your searches`
                        : "Nothing new in your searches"}
                </h1>
                <div style={meta}>
                  {lastChecked ? `Last checked ${relativeTime(lastChecked)}` : "Not checked from here yet"}
                  {laterCount > 0 && ` · ${laterCount} set aside for later`}
                  {newTotal > newShown && ` · showing ${newShown} today`}
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button style={btn} onClick={checkForNewRoles} disabled={checking}>
                  {checking ? "Checking company job boards…" : "Check for new roles"}
                </button>
                {startLabel && (
                  <button style={btnPrimary} onClick={start}>{startLabel}</button>
                )}
              </div>
            </div>
            {checking && (
              <p style={note}>This polls every company board letsA(ppl)I follows. It can take a minute or two.</p>
            )}
            {checkResult && !checking && <p style={note}>{checkResult}</p>}

            {searches && searches.length === 0 && (
              <div style={{ ...card, marginTop: 24 }}>
                <p style={{ margin: "0 0 6px", fontWeight: 600 }}>Save a search to start</p>
                <p style={{ margin: "0 0 14px", color: "#555" }}>
                  Run a search, then choose “Save this search”. Today shows only roles that are new in your saved
                  searches, a few at a time.
                </p>
                <button style={btn} onClick={onOpenSearch}>Go to search</button>
              </div>
            )}

            {searches && searches.length > 0 && (
              <div style={{ marginTop: 20 }}>
                {searches.map((s) => (
                  <div key={s.id} style={searchRow}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 500 }}>{s.name}</div>
                      <div style={meta}>
                        {s.open_count} open
                        {s.top_companies.length > 0 &&
                          ` · ${s.top_companies.join(", ")}${s.company_count > s.top_companies.length ? ` and ${s.company_count - s.top_companies.length} more` : ""}`}
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      {s.new_count > 0 ? <span style={newBadge}>{s.new_count} new</span> : <span style={meta}>nothing new</span>}
                      <button style={linkBtn} onClick={() => removeSearch(s.id)} aria-label={`Remove ${s.name}`}>Remove</button>
                    </div>
                  </div>
                ))}
                <div style={{ ...searchRow, borderBottom: "none" }}>
                  <button style={{ ...linkBtn, color: "#185fa5" }} onClick={onOpenSearch}>+ Save another search</button>
                </div>
              </div>
            )}
          </>
        )}

        {stage === "focus" && current && (
          <>
            <div style={{ display: "flex", justifyContent: "space-between", ...meta }}>
              <span>
                {index + 1} of {items.length} ·{" "}
                {current.source.type === "later" ? "set aside last time" : `from “${current.source.name}”`}
              </span>
              <button style={linkBtn} onClick={leaveFocus}>Leave (Esc)</button>
            </div>
            <div style={progressTrack}>
              <div style={{ ...progressFill, width: `${(index / items.length) * 100}%` }} />
            </div>

            <div style={card}>
              <div style={meta}>
                {[current.company, current.locations.join(" · "), current.first_seen_at && `first seen ${relativeTime(current.first_seen_at)}`]
                  .filter(Boolean)
                  .join(" · ")}
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 600, margin: "6px 0 10px", color: "#111827" }}>{current.title}</h2>
              {current.signals.length > 0 && (
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {current.signals.map((s) => (
                    <span key={s} style={chip}>{signalLabel(s)}</span>
                  ))}
                </div>
              )}
              <p style={{ ...note, marginTop: 14 }}>
                Want to know what the work involves?{" "}
                <button style={{ ...linkBtn, color: "#185fa5", padding: 0 }} onClick={() => onOpenInApp(current)}>
                  Open it in letsA(ppl)I
                </button>{" "}
                to read the posting and analyze it.
              </p>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16 }}>
              <button style={btnPrimary} onClick={() => decide("saved")} disabled={deciding}>Save <kbd style={kbdDark}>S</kbd></button>
              <button style={btn} onClick={() => decide("ignored")} disabled={deciding}>Skip <kbd style={kbd}>K</kbd></button>
              <button style={btn} onClick={openPosting}>Open posting <kbd style={kbd}>O</kbd></button>
              <button style={{ ...btn, marginLeft: "auto" }} onClick={() => decide("later")} disabled={deciding}>
                Later <kbd style={kbd}>L</kbd>
              </button>
            </div>
          </>
        )}

        {stage === "done" && (
          <div style={{ textAlign: "center", paddingTop: 24 }}>
            <h1 style={h1}>You're caught up</h1>
            <p style={meta}>
              {newTotal > newShown
                ? `That's today's set. ${newTotal - newShown} more new ${newTotal - newShown === 1 ? "role is" : "roles are"} waiting for next time.`
                : "That's everything new in your saved searches."}
            </p>
            <div style={stats}>
              {(["saved", "ignored", "later"] as Decision[]).map((d) => (
                <div key={d} style={statBox}>
                  <div style={meta}>{d === "saved" ? "Saved" : d === "ignored" ? "Skipped" : "Later"}</div>
                  <div style={{ fontSize: 24, fontWeight: 600 }}>{tally[d]}</div>
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap" }}>
              <button style={btnPrimary} onClick={onOpenSaved}>Review saved roles</button>
              <button style={btn} onClick={onOpenSearch}>Search everything</button>
              <button style={btn} onClick={leaveFocus}>Back to Today</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const page: React.CSSProperties = { flex: 1, height: "100vh", overflowY: "auto", background: "#fafafa", color: "#1f2937" };
const topBar: React.CSSProperties = { display: "flex", gap: 6, padding: "14px 24px", borderBottom: "1px solid #eee", background: "#fff", position: "sticky", top: 0 };
const tab: React.CSSProperties = { border: "1px solid transparent", background: "transparent", borderRadius: 8, padding: "6px 12px", fontSize: 14, fontWeight: 600, color: "#4b5563", cursor: "pointer" };
const tabActive: React.CSSProperties = { background: "#f0f7ff", borderColor: "#dbe7f7", color: "#111827" };
const column: React.CSSProperties = { maxWidth: 720, margin: "0 auto", padding: "40px 24px 80px" };
const h1: React.CSSProperties = { fontSize: 24, fontWeight: 600, margin: "0 0 4px", color: "#111827" };
const meta: React.CSSProperties = { fontSize: 13, color: "#6b7280" };
const note: React.CSSProperties = { fontSize: 13, color: "#4b5563", borderLeft: "3px solid #e5e7eb", paddingLeft: 10, margin: "14px 0 0" };
const errorText: React.CSSProperties = { color: "#b42318", fontSize: 14, margin: "0 0 12px" };
const card: React.CSSProperties = { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: "18px 20px" };
const searchRow: React.CSSProperties = { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, padding: "14px 2px", borderBottom: "1px solid #eee" };
const newBadge: React.CSSProperties = { fontSize: 12, padding: "2px 9px", borderRadius: 8, background: "#e6f1fb", color: "#185fa5", fontWeight: 600, whiteSpace: "nowrap" };
const chip: React.CSSProperties = { fontSize: 12, padding: "3px 9px", borderRadius: 8, border: "1px solid #e5e7eb", background: "#f9fafb", color: "#4b5563" };
const btn: React.CSSProperties = { padding: "9px 14px", borderRadius: 9, border: "1px solid #d1d5db", background: "#fff", fontSize: 14, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 8 };
const btnPrimary: React.CSSProperties = { ...btn, background: "#111827", color: "#fff", borderColor: "#111827" };
const linkBtn: React.CSSProperties = { border: "none", background: "transparent", color: "#6b7280", fontSize: 13, cursor: "pointer", padding: 0 };
const kbd: React.CSSProperties = { font: "12px ui-monospace, monospace", border: "1px solid #d1d5db", borderRadius: 4, padding: "0 5px", color: "#6b7280" };
const kbdDark: React.CSSProperties = { ...kbd, color: "#e5e7eb", borderColor: "#6b7280" };
const progressTrack: React.CSSProperties = { height: 4, background: "#e5e7eb", borderRadius: 4, overflow: "hidden", margin: "8px 0 18px" };
const progressFill: React.CSSProperties = { height: "100%", background: "#185fa5", transition: "width 0.2s ease" };
const stats: React.CSSProperties = { display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10, margin: "20px 0", textAlign: "left" };
const statBox: React.CSSProperties = { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 10, padding: 12 };
