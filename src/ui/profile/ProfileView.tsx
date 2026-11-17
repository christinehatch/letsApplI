import React, { useCallback, useEffect, useRef, useState } from "react";

/**
 * Milestone 6.1 — the user's profile. Everything here is added by the user
 * and stays on this machine; nothing on this page calls an AI service.
 */

type SourceKind = "resume" | "linkedin" | "transcript" | "website";

type Source = {
  id: number;
  kind: SourceKind;
  label: string;
  url: string | null;
  has_file: boolean;
  added_at: string;
  read_at: string | null;
  text_chars: number;
  text_preview: string;
};

type Preferences = {
  location: string[];
  work_mode: string[];
  level: string[];
  company_size: string[];
  industry_in: string[];
  industry_out: string[];
};

const EMPTY_PREFS: Preferences = {
  location: [],
  work_mode: [],
  level: [],
  company_size: [],
  industry_in: [],
  industry_out: [],
};

const DOCUMENTS: { kind: Exclude<SourceKind, "website">; title: string; hint: string }[] = [
  { kind: "resume", title: "Resume", hint: "PDF or Word." },
  {
    kind: "linkedin",
    title: "LinkedIn",
    hint: "On your LinkedIn profile, choose More → Save to PDF, then upload that file here.",
  },
  { kind: "transcript", title: "Transcripts", hint: "PDF. Unofficial copies are fine." },
];

const WORK_MODES = [
  ["remote", "Remote"],
  ["hybrid", "Hybrid"],
  ["onsite", "On-site"],
] as const;
const LEVELS = [
  ["intern", "Intern"],
  ["entry", "Entry"],
  ["mid", "Mid"],
  ["senior", "Senior"],
  ["staff", "Staff"],
  ["principal", "Principal"],
  ["manager", "Manager"],
  ["director", "Director"],
] as const;
const COMPANY_SIZES = [
  ["startup", "Startup"],
  ["small", "Small"],
  ["mid", "Mid-size"],
  ["large", "Large"],
] as const;

function addedOn(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function ProfileView({
  apiUrl,
  onOpenToday,
  onOpenSearch,
  onOpenSaved,
}: {
  apiUrl: (path: string) => string;
  onOpenToday: () => void;
  onOpenSearch: () => void;
  onOpenSaved: () => void;
}) {
  const [sources, setSources] = useState<Source[] | null>(null);
  const [skills, setSkills] = useState<string[]>([]);
  const [prefs, setPrefs] = useState<Preferences>(EMPTY_PREFS);
  const [error, setError] = useState<string | null>(null);
  const [savedNote, setSavedNote] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await fetch(apiUrl("/api/profile"));
      if (res.status === 404) {
        throw new Error("The API server is running an older version. Restart bridge_server.py to use your profile.");
      }
      if (!res.ok) throw new Error("Couldn't load your profile.");
      const data = await res.json();
      setSources(data.sources ?? []);
      setSkills(data.skills ?? []);
      setPrefs({ ...EMPTY_PREFS, ...(data.preferences ?? {}) });
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't load your profile.");
      setSources([]);
    }
  }, [apiUrl]);

  useEffect(() => {
    load();
  }, [load]);

  const flashSaved = (what: string) => {
    setSavedNote(`${what} saved`);
    window.setTimeout(() => setSavedNote(null), 1800);
  };

  const saveSkills = async (next: string[]) => {
    setSkills(next);
    try {
      const res = await fetch(apiUrl("/api/profile/skills"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skills: next }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Couldn't save your skills.");
      setSkills(data.skills);
      flashSaved("Skills");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't save your skills.");
    }
  };

  const savePrefs = async (next: Preferences) => {
    setPrefs(next);
    try {
      const res = await fetch(apiUrl("/api/profile/preferences"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Couldn't save your preferences.");
      setPrefs({ ...EMPTY_PREFS, ...data.preferences });
      flashSaved("Preferences");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't save your preferences.");
    }
  };

  const removeSource = async (source: Source) => {
    const what = source.kind === "website" ? source.url : source.label;
    if (!window.confirm(`Remove “${what}”? The file and everything read from it will be deleted.`)) return;
    const res = await fetch(apiUrl(`/api/profile/sources/${source.id}`), { method: "DELETE" });
    if (!res.ok && res.status !== 404) {
      setError("Couldn't remove that.");
      return;
    }
    setSources((prev) => (prev ?? []).filter((s) => s.id !== source.id));
  };

  const addSource = (source: Source) => setSources((prev) => [source, ...(prev ?? [])]);

  const setPref = (kind: keyof Preferences, values: string[]) => savePrefs({ ...prefs, [kind]: values });

  return (
    <div style={page}>
      <nav style={topBar}>
        <button style={tab} onClick={onOpenToday}>Today</button>
        <button style={tab} onClick={onOpenSearch}>Search</button>
        <button style={tab} onClick={onOpenSaved}>Saved jobs</button>
        <span style={{ ...tab, ...tabActive }}>Profile</span>
        <span style={{ flex: 1 }} />
        {savedNote && <span style={{ fontSize: 13, color: "#047857", alignSelf: "center" }}>{savedNote}</span>}
      </nav>

      <div style={column}>
        <h1 style={h1}>Your profile</h1>
        <p style={meta}>
          What you add here is stored only on this computer, and nothing on this page is sent to an AI. You can see
          exactly what was read from each file, and remove anything.
        </p>
        {error && <p style={errorText}>{error}</p>}

        <section style={section}>
          <h2 style={h2}>Documents</h2>
          {DOCUMENTS.map((doc) => (
            <DocumentRow
              key={doc.kind}
              apiUrl={apiUrl}
              kind={doc.kind}
              title={doc.title}
              hint={doc.hint}
              sources={(sources ?? []).filter((s) => s.kind === doc.kind)}
              onAdded={addSource}
              onRemove={removeSource}
            />
          ))}
        </section>

        <section style={section}>
          <h2 style={h2}>Personal website</h2>
          <WebsiteRow
            apiUrl={apiUrl}
            sources={(sources ?? []).filter((s) => s.kind === "website")}
            onAdded={addSource}
            onRemove={removeSource}
          />
        </section>

        <section style={section}>
          <h2 style={h2}>Skills and tools</h2>
          <p style={hintText}>Languages, tools, methods — anything you'd want a role to use.</p>
          <ChipInput values={skills} onChange={saveSkills} placeholder="Type a skill and press Enter" label="Skills and tools" />
        </section>

        <section style={section}>
          <h2 style={h2}>Where and how you want to work</h2>

          <Field label="Locations">
            <ChipInput
              values={prefs.location}
              onChange={(v) => setPref("location", v)}
              placeholder="e.g. San Francisco, Remote"
              label="Locations"
            />
          </Field>
          <Field label="Work setup">
            <Toggles options={WORK_MODES} values={prefs.work_mode} onChange={(v) => setPref("work_mode", v)} />
          </Field>
          <Field label="Level">
            <Toggles options={LEVELS} values={prefs.level} onChange={(v) => setPref("level", v)} />
          </Field>
          <Field label="Company size">
            <Toggles options={COMPANY_SIZES} values={prefs.company_size} onChange={(v) => setPref("company_size", v)} />
          </Field>
          <Field label="Industries you'd like">
            <ChipInput
              values={prefs.industry_in}
              onChange={(v) => setPref("industry_in", v)}
              placeholder="e.g. health tech, climate"
              label="Industries you'd like"
            />
          </Field>
          <Field label="Industries to avoid">
            <ChipInput
              values={prefs.industry_out}
              onChange={(v) => setPref("industry_out", v)}
              placeholder="e.g. gambling"
              label="Industries to avoid"
            />
          </Field>
        </section>

        <p style={{ ...meta, marginTop: 28 }}>
          Coming next: a “Read it” button that suggests facts from your documents for you to confirm, and
          recommendations based on your profile.
        </p>
      </div>
    </div>
  );
}

// ------------------------------------------------------------
// Documents
// ------------------------------------------------------------

function DocumentRow({
  apiUrl,
  kind,
  title,
  hint,
  sources,
  onAdded,
  onRemove,
}: {
  apiUrl: (path: string) => string;
  kind: string;
  title: string;
  hint: string;
  sources: Source[];
  onAdded: (s: Source) => void;
  onRemove: (s: Source) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [rowError, setRowError] = useState<string | null>(null);

  const upload = async (file: File) => {
    setUploading(true);
    setRowError(null);
    try {
      const params = new URLSearchParams({ kind, filename: file.name });
      const res = await fetch(apiUrl(`/api/profile/sources/upload?${params}`), {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: file,
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Couldn't upload that file.");
      onAdded(data.source);
    } catch (e) {
      setRowError(e instanceof Error ? e.message : "Couldn't upload that file.");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div style={row}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div>
          <div style={rowTitle}>{title}</div>
          <div style={hintText}>{hint}</div>
        </div>
        <button style={btn} onClick={() => inputRef.current?.click()} disabled={uploading}>
          {uploading ? "Reading…" : sources.length ? "Add another" : "Upload"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
          style={{ display: "none" }}
          aria-label={`Upload ${title}`}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) upload(file);
          }}
        />
      </div>
      {rowError && <div style={rowErrorText}>{rowError}</div>}
      {sources.map((s) => (
        <SourceItem key={s.id} apiUrl={apiUrl} source={s} onRemove={onRemove} />
      ))}
    </div>
  );
}

function SourceItem({
  apiUrl,
  source,
  onRemove,
}: {
  apiUrl: (path: string) => string;
  source: Source;
  onRemove: (s: Source) => void;
}) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState<string | null>(null);

  const toggle = async () => {
    if (!open && text === null) {
      const res = await fetch(apiUrl(`/api/profile/sources/${source.id}/text`));
      const data = await res.json().catch(() => null);
      setText(res.ok ? data?.source?.text ?? "" : "Couldn't load the text.");
    }
    setOpen((v) => !v);
  };

  return (
    <div style={sourceItem}>
      <div style={{ display: "flex", gap: 10, alignItems: "baseline", flexWrap: "wrap" }}>
        <span style={{ fontWeight: 600, color: "#111827", wordBreak: "break-word" }}>
          {source.kind === "website" && source.url ? (
            <a href={source.url} target="_blank" rel="noreferrer" style={{ color: "#185fa5" }}>{source.url}</a>
          ) : (
            source.label
          )}
        </span>
        <span style={meta}>
          added {addedOn(source.added_at)}
          {source.kind === "website"
            ? " · saved as a link, not read yet"
            : ` · ${source.text_chars.toLocaleString()} characters read`}
        </span>
        <span style={{ flex: 1 }} />
        {source.kind !== "website" && (
          <button style={linkBtn} onClick={toggle} aria-expanded={open}>
            {open ? "Hide text" : "See what was read"}
          </button>
        )}
        <button style={{ ...linkBtn, color: "#b42318" }} onClick={() => onRemove(source)}>
          Remove
        </button>
      </div>
      {open && <pre style={textBox}>{text ?? "Loading…"}</pre>}
    </div>
  );
}

function WebsiteRow({
  apiUrl,
  sources,
  onAdded,
  onRemove,
}: {
  apiUrl: (path: string) => string;
  sources: Source[];
  onAdded: (s: Source) => void;
  onRemove: (s: Source) => void;
}) {
  const [url, setUrl] = useState("");
  const [saving, setSaving] = useState(false);
  const [rowError, setRowError] = useState<string | null>(null);

  const add = async () => {
    if (!url.trim()) return;
    setSaving(true);
    setRowError(null);
    try {
      const res = await fetch(apiUrl("/api/profile/sources/website"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Couldn't add that link.");
      onAdded(data.source);
      setUrl("");
    } catch (e) {
      setRowError(e instanceof Error ? e.message : "Couldn't add that link.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={row}>
      <div style={hintText}>Saved as a link. The page is only read when you choose to.</div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          add();
        }}
        style={{ display: "flex", gap: 8, marginTop: 8 }}
      >
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="yourname.com"
          aria-label="Website address"
          style={{ ...input, flex: 1 }}
        />
        <button type="submit" style={btn} disabled={saving || !url.trim()}>
          Add
        </button>
      </form>
      {rowError && <div style={rowErrorText}>{rowError}</div>}
      {sources.map((s) => (
        <SourceItem key={s.id} apiUrl={apiUrl} source={s} onRemove={onRemove} />
      ))}
    </div>
  );
}

// ------------------------------------------------------------
// Inputs
// ------------------------------------------------------------

function ChipInput({
  values,
  onChange,
  placeholder,
  label,
}: {
  values: string[];
  onChange: (next: string[]) => void;
  placeholder: string;
  label: string;
}) {
  const [draft, setDraft] = useState("");

  const commit = () => {
    const parts = draft
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean);
    setDraft("");
    const lower = new Set(values.map((v) => v.toLowerCase()));
    const fresh = parts.filter((p) => !lower.has(p.toLowerCase()));
    if (fresh.length) onChange([...values, ...fresh]);
  };

  return (
    <div style={chipBox}>
      {values.map((v) => (
        <span key={v} style={chip}>
          {v}
          <button
            type="button"
            onClick={() => onChange(values.filter((x) => x !== v))}
            style={chipX}
            aria-label={`Remove ${v}`}
          >
            ×
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            commit();
          } else if (e.key === "Backspace" && !draft && values.length) {
            onChange(values.slice(0, -1));
          }
        }}
        onBlur={commit}
        placeholder={values.length ? "" : placeholder}
        aria-label={label}
        style={{ border: "none", outline: "none", flex: 1, minWidth: 160, fontSize: 14, padding: "4px 2px", background: "transparent" }}
      />
    </div>
  );
}

function Toggles({
  options,
  values,
  onChange,
}: {
  options: readonly (readonly [string, string])[];
  values: string[];
  onChange: (next: string[]) => void;
}) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
      {options.map(([value, label]) => {
        const on = values.includes(value);
        return (
          <button
            key={value}
            type="button"
            aria-pressed={on}
            onClick={() => onChange(on ? values.filter((v) => v !== value) : [...values, value])}
            style={{
              padding: "5px 12px",
              borderRadius: 999,
              border: `1px solid ${on ? "#111827" : "#d1d5db"}`,
              background: on ? "#111827" : "#fff",
              color: on ? "#fff" : "#374151",
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 14 }}>
      <div style={fieldLabel}>{label}</div>
      {children}
    </div>
  );
}

// ------------------------------------------------------------
// Styles (match TodayView)
// ------------------------------------------------------------

const page: React.CSSProperties = { flex: 1, height: "100vh", overflowY: "auto", background: "#fafafa", color: "#1f2937" };
const topBar: React.CSSProperties = { display: "flex", gap: 6, padding: "14px 24px", borderBottom: "1px solid #eee", background: "#fff", position: "sticky", top: 0, zIndex: 1 };
const tab: React.CSSProperties = { border: "1px solid transparent", background: "transparent", borderRadius: 8, padding: "6px 12px", fontSize: 14, fontWeight: 600, color: "#4b5563", cursor: "pointer" };
const tabActive: React.CSSProperties = { background: "#f0f7ff", borderColor: "#dbe7f7", color: "#111827" };
const column: React.CSSProperties = { maxWidth: 720, margin: "0 auto", padding: "40px 24px 80px" };
const h1: React.CSSProperties = { fontSize: 24, fontWeight: 600, margin: "0 0 6px", color: "#111827" };
const h2: React.CSSProperties = { fontSize: 16, fontWeight: 600, margin: "0 0 8px", color: "#111827" };
const meta: React.CSSProperties = { fontSize: 13, color: "#6b7280", margin: 0, lineHeight: 1.5 };
const hintText: React.CSSProperties = { fontSize: 13, color: "#6b7280", lineHeight: 1.5 };
const rowErrorText: React.CSSProperties = { color: "#b42318", fontSize: 13, marginTop: 8, lineHeight: 1.5 };
const errorText: React.CSSProperties = { color: "#b42318", fontSize: 14, margin: "12px 0 0" };
const section: React.CSSProperties = { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: "18px 20px", marginTop: 20 };
const row: React.CSSProperties = { padding: "12px 0", borderTop: "1px solid #f1f1f1" };
const rowTitle: React.CSSProperties = { fontSize: 14, fontWeight: 600, color: "#111827" };
const sourceItem: React.CSSProperties = { marginTop: 10, padding: "8px 10px", background: "#f9fafb", border: "1px solid #eef0f2", borderRadius: 8, fontSize: 14 };
const textBox: React.CSSProperties = { marginTop: 8, maxHeight: 280, overflow: "auto", whiteSpace: "pre-wrap", fontFamily: "inherit", fontSize: 13, color: "#374151", background: "#fff", border: "1px solid #e5e7eb", borderRadius: 6, padding: 10 };
const fieldLabel: React.CSSProperties = { fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 };
const input: React.CSSProperties = { padding: "8px 10px", borderRadius: 8, border: "1px solid #d1d5db", fontSize: 14 };
const chipBox: React.CSSProperties = { display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center", border: "1px solid #d1d5db", borderRadius: 8, padding: "6px 8px", background: "#fff" };
const chip: React.CSSProperties = { display: "inline-flex", alignItems: "center", gap: 4, fontSize: 13, padding: "3px 4px 3px 10px", borderRadius: 999, background: "#eef2f7", color: "#1f2937" };
const chipX: React.CSSProperties = { border: "none", background: "transparent", cursor: "pointer", color: "#6b7280", fontSize: 15, lineHeight: 1, padding: "0 4px" };
const btn: React.CSSProperties = { padding: "7px 12px", borderRadius: 8, border: "1px solid #d1d5db", background: "#fff", fontSize: 13, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" };
const linkBtn: React.CSSProperties = { border: "none", background: "transparent", color: "#185fa5", fontSize: 13, cursor: "pointer", padding: 0 };
