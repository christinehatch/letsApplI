import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

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

type FactKind = "title" | "skill" | "domain" | "education" | "location" | "achievement";

type Fact = {
  id: number;
  source_id: number;
  kind: FactKind;
  text: string;
  quote: string | null;
  status: "proposed" | "confirmed";
};

const FACT_KIND_LABELS: Record<FactKind, string> = {
  title: "Roles",
  skill: "Skills",
  domain: "Fields",
  education: "Education",
  location: "Places",
  achievement: "Things you did",
};
const FACT_KIND_ORDER: FactKind[] = ["title", "skill", "domain", "education", "location", "achievement"];

const CONSENT_KEY = "letsappli.profileReadConsent.v1";

/** Shared by every source on the page: its facts, and the one-time AI notice. */
const FactsContext = createContext<{
  facts: Fact[];
  setSourceFacts: (sourceId: number, facts: Fact[]) => void;
  updateFact: (fact: Fact) => void;
  updateSource: (source: Source) => void;
  askConsent: (sourceId: number) => Promise<boolean>;
  consentFor: number | null;
  answerConsent: (ok: boolean) => void;
}>({
  facts: [],
  setSourceFacts: () => {},
  updateFact: () => {},
  updateSource: () => {},
  askConsent: async () => false,
  consentFor: null,
  answerConsent: () => {},
});

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
  { kind: "linkedin", title: "LinkedIn", hint: "" }, // rendered by LinkedInRow
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
  const [facts, setFacts] = useState<Fact[]>([]);
  const [consentAsk, setConsentAsk] = useState<{ sourceId: number; answer: (ok: boolean) => void } | null>(null);
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
      setFacts(data.facts ?? []);
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
    setFacts((prev) => prev.filter((f) => f.source_id !== source.id));
  };

  const addSource = (source: Source) => setSources((prev) => [source, ...(prev ?? [])]);

  const factsApi = {
    facts,
    setSourceFacts: (sourceId: number, next: Fact[]) =>
      setFacts((prev) => [...prev.filter((f) => f.source_id !== sourceId), ...next]),
    updateFact: (fact: Fact) =>
      setFacts((prev) =>
        (fact.status as string) === "rejected"
          ? prev.filter((f) => f.id !== fact.id)
          : prev.map((f) => (f.id === fact.id ? fact : f)),
      ),
    updateSource: (source: Source) =>
      setSources((prev) => (prev ?? []).map((s) => (s.id === source.id ? source : s))),
    consentFor: consentAsk?.sourceId ?? null,
    answerConsent: (ok: boolean) => consentAsk?.answer(ok),
    askConsent: (sourceId: number) => {
      try {
        if (window.localStorage.getItem(CONSENT_KEY) === "yes") return Promise.resolve(true);
      } catch {
        /* storage unavailable: ask every time */
      }
      return new Promise<boolean>((resolve) => {
        setConsentAsk({ sourceId, answer: (ok: boolean) => {
          setConsentAsk(null);
          if (ok) {
            try {
              window.localStorage.setItem(CONSENT_KEY, "yes");
            } catch {
              /* ignore */
            }
          }
          resolve(ok);
        } });
      });
    },
  };

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

      <FactsContext.Provider value={factsApi}>
      <div style={column}>
        <h1 style={h1}>Your profile</h1>
        <p style={meta}>
          What you add here is stored only on this computer. A document's text goes to the AI service only when you
          press <b>Read it</b> on that document, and nothing it suggests joins your profile until you keep it.
        </p>
        {error && <p style={errorText}>{error}</p>}

        <section style={section}>
          <h2 style={h2}>Documents</h2>
          {DOCUMENTS.map((doc) =>
            doc.kind === "linkedin" ? (
              <LinkedInRow
                key="linkedin"
                apiUrl={apiUrl}
                sources={(sources ?? []).filter((s) => s.kind === "linkedin")}
                onAdded={addSource}
                onReplaced={(source) =>
                  setSources((prev) => [
                    source,
                    ...(prev ?? []).filter((s) => !(s.kind === "linkedin" && !s.has_file)),
                  ])
                }
                onRemove={removeSource}
              />
            ) : (
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
            ),
          )}
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

        <p style={{ ...meta, marginTop: 28 }}>Coming next: roles recommended from your profile.</p>
      </div>
      </FactsContext.Provider>
    </div>
  );
}

function ConsentNotice({ onAnswer }: { onAnswer: (ok: boolean) => void }) {
  return (
    <div role="dialog" aria-label="Before reading" style={consentBox}>
      <div style={{ fontWeight: 600, color: "#111827", marginBottom: 6 }}>Before letsA(ppl)I reads this</div>
      <div style={{ ...hintText, color: "#374151" }}>
        Reading sends this document's text (or, for a website, that page and up to 5 pages it links to on the same site) to OpenAI's API to suggest facts like
        your roles, skills and education. Grades are left out. Nothing is added to your profile until you keep it,
        and you'll only see this note once.
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button style={{ ...btn, background: "#111827", color: "#fff", borderColor: "#111827" }} onClick={() => onAnswer(true)}>
          Read it
        </button>
        <button style={btn} onClick={() => onAnswer(false)}>Cancel</button>
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
  nested = false,
}: {
  apiUrl: (path: string) => string;
  kind: string;
  title: string;
  hint: string;
  sources: Source[];
  onAdded: (s: Source) => void;
  onRemove: (s: Source) => void;
  nested?: boolean;
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
    <div style={nested ? { padding: "10px 0 0", borderTop: "1px dashed #e5e7eb" } : row}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div>
          <div style={nested ? { ...rowTitle, fontSize: 13 } : rowTitle}>{title}</div>
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
  const ctx = useContext(FactsContext);
  const [open, setOpen] = useState(false);
  const [text, setText] = useState<string | null>(null);
  const [reading, setReading] = useState(false);
  const [readError, setReadError] = useState<string | null>(null);
  const [readNote, setReadNote] = useState<string | null>(null);

  const mine = ctx.facts.filter((f) => f.source_id === source.id);
  const proposed = mine.filter((f) => f.status === "proposed");
  const confirmed = mine.filter((f) => f.status === "confirmed");
  const isWebsite = source.kind === "website";
  const isLinkedInLink = source.kind === "linkedin" && !source.has_file;
  const isWebsiteLink = isWebsite && !source.has_file;
  const isLink = isWebsiteLink || isLinkedInLink;

  const toggle = async () => {
    if (!open && text === null) {
      const res = await fetch(apiUrl(`/api/profile/sources/${source.id}/text`));
      const data = await res.json().catch(() => null);
      setText(res.ok ? data?.source?.text ?? "" : "Couldn't load the text.");
    }
    setOpen((v) => !v);
  };

  const read = async () => {
    if (!(await ctx.askConsent(source.id))) return;
    setReading(true);
    setReadError(null);
    setReadNote(null);
    try {
      const res = await fetch(apiUrl(`/api/profile/sources/${source.id}/read`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consent: true }),
      });
      const data = await res.json().catch(() => null);
      if (res.status === 404 && !data?.detail?.includes("Source")) {
        throw new Error("The API server is running an older version. Restart bridge_server.py to read documents.");
      }
      if (!res.ok) throw new Error(data?.detail || "Couldn't read this.");
      ctx.updateSource(data.source);
      ctx.setSourceFacts(source.id, data.facts);
      setText(null); // websites get fresh text
      const parts = [
        data.proposed === 0
          ? "Nothing new to suggest."
          : `${data.proposed} suggestion${data.proposed === 1 ? "" : "s"} to check below.`,
      ];
      if (data.dropped > 0) {
        parts.push(`${data.dropped} left out because they weren't in the text as written.`);
      }
      const pages: string[] = Array.isArray(data.pages_read) ? data.pages_read : [];
      if (pages.length > 0) {
        const paths = pages.map((u) => {
          try {
            return new URL(u).pathname || "/";
          } catch {
            return u;
          }
        });
        parts.unshift(`Read ${pages.length} page${pages.length === 1 ? "" : "s"}: ${paths.join(", ")}.`);
      }
      setReadNote(parts.join(" "));
    } catch (e) {
      setReadError(e instanceof Error ? e.message : "Couldn't read this.");
    } finally {
      setReading(false);
    }
  };

  const patch = async (fact: Fact, body: { status?: string; text?: string }) => {
    const res = await fetch(apiUrl(`/api/profile/facts/${fact.id}`), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      setReadError(data?.detail || "Couldn't save that.");
      return;
    }
    ctx.updateFact(data.fact);
  };

  const keepAll = async () => {
    const res = await fetch(apiUrl(`/api/profile/sources/${source.id}/confirm-all`), { method: "POST" });
    const data = await res.json().catch(() => null);
    if (res.ok) ctx.setSourceFacts(source.id, data.facts);
  };

  const status = isLinkedInLink
    ? "saved as a link · LinkedIn can't be read automatically"
    : isWebsiteLink
    ? source.read_at
      ? `read ${addedOn(source.read_at)} · ${source.text_chars.toLocaleString()} characters`
      : "saved as a link, not read yet"
    : `${source.text_chars.toLocaleString()} characters read`;

  return (
    <div style={sourceItem}>
      <div style={{ display: "flex", gap: 10, alignItems: "baseline", flexWrap: "wrap" }}>
        <span style={{ fontWeight: 600, color: "#111827", wordBreak: "break-word" }}>
          {isLink && source.url ? (
            <a href={source.url} target="_blank" rel="noreferrer" style={{ color: "#185fa5" }}>{source.url}</a>
          ) : (
            source.label
          )}
        </span>
        <span style={meta}>added {addedOn(source.added_at)} · {status}</span>
        <span style={{ flex: 1 }} />
        {!isLinkedInLink && (
          <button style={{ ...linkBtn, fontWeight: 600 }} onClick={read} disabled={reading}>
            {reading ? "Reading…" : source.read_at ? "Read again" : "Read it"}
          </button>
        )}
        {source.text_chars > 0 && (
          <button style={linkBtn} onClick={toggle} aria-expanded={open}>
            {open ? "Hide text" : "See what was read"}
          </button>
        )}
        <button style={{ ...linkBtn, color: "#b42318" }} onClick={() => onRemove(source)}>
          Remove
        </button>
      </div>
      {ctx.consentFor === source.id && <ConsentNotice onAnswer={ctx.answerConsent} />}
      {readError && <div style={rowErrorText}>{readError}</div>}
      {readNote && <div style={{ ...hintText, marginTop: 6 }}>{readNote}</div>}
      {open && <pre style={textBox}>{text ?? "Loading…"}</pre>}

      {proposed.length > 0 && (
        <div style={reviewBox}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
            <div style={{ fontWeight: 600, color: "#111827" }}>Suggested from this {isWebsiteLink ? "site" : "file"}</div>
            <button style={btn} onClick={keepAll}>Keep all {proposed.length}</button>
          </div>
          <div style={{ ...hintText, marginBottom: 6 }}>Check each one. Only what you keep joins your profile.</div>
          {FACT_KIND_ORDER.filter((k) => proposed.some((f) => f.kind === k)).map((kind) => (
            <div key={kind} style={{ marginTop: 10 }}>
              <div style={fieldLabel}>{FACT_KIND_LABELS[kind]}</div>
              {proposed
                .filter((f) => f.kind === kind)
                .map((f) => (
                  <ProposedFact
                    key={f.id}
                    fact={f}
                    onKeep={(text) => patch(f, text === f.text ? { status: "confirmed" } : { status: "confirmed", text })}
                    onReject={() => patch(f, { status: "rejected" })}
                  />
                ))}
            </div>
          ))}
        </div>
      )}

      {confirmed.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div style={{ ...hintText, marginBottom: 4 }}>In your profile from this {isWebsiteLink ? "site" : "file"}:</div>
          {FACT_KIND_ORDER.filter((k) => confirmed.some((f) => f.kind === k)).map((kind) => (
            <div key={kind} style={{ display: "flex", gap: 6, alignItems: "flex-start", marginTop: 4 }}>
              <span style={{ fontSize: 12, color: "#6b7280", width: 92, flexShrink: 0, paddingTop: 4 }}>{FACT_KIND_LABELS[kind]}</span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, flex: 1, minWidth: 0 }}>
              {confirmed
                .filter((f) => f.kind === kind)
                .map((f) => (
                  <span key={f.id} style={chip} title={f.quote ? `From: “${f.quote}”` : undefined}>
                    {f.text}
                    <button
                      type="button"
                      onClick={() => patch(f, { status: "rejected" })}
                      style={chipX}
                      aria-label={`Remove ${f.text} from your profile`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ProposedFact({
  fact,
  onKeep,
  onReject,
}: {
  fact: Fact;
  onKeep: (text: string) => void;
  onReject: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(fact.text);

  return (
    <div style={proposedRow}>
      <div style={{ flex: 1, minWidth: 0 }}>
        {editing ? (
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && draft.trim()) onKeep(draft.trim());
              if (e.key === "Escape") {
                setDraft(fact.text);
                setEditing(false);
              }
            }}
            aria-label={`Edit ${fact.text}`}
            autoFocus
            style={{ ...input, width: "100%", boxSizing: "border-box" }}
          />
        ) : (
          <div style={{ color: "#111827" }}>{fact.text}</div>
        )}
        {fact.quote && fact.quote.toLowerCase() !== fact.text.toLowerCase() && (
          <div style={quoteText}>“{fact.quote}”</div>
        )}
      </div>
      <div style={{ display: "flex", gap: 10, flexShrink: 0 }}>
        <button style={{ ...linkBtn, fontWeight: 600, color: "#047857" }} onClick={() => onKeep(editing ? draft.trim() || fact.text : fact.text)}>
          Keep
        </button>
        {!editing && (
          <button style={linkBtn} onClick={() => setEditing(true)}>
            Edit
          </button>
        )}
        <button style={{ ...linkBtn, color: "#6b7280" }} onClick={onReject}>
          Not right
        </button>
      </div>
    </div>
  );
}

function LinkedInRow({
  apiUrl,
  sources,
  onAdded,
  onReplaced,
  onRemove,
}: {
  apiUrl: (path: string) => string;
  sources: Source[];
  onAdded: (s: Source) => void;
  onReplaced: (s: Source) => void;
  onRemove: (s: Source) => void;
}) {
  const link = sources.find((s) => !s.has_file) ?? null;
  const pdfs = sources.filter((s) => s.has_file);
  const [url, setUrl] = useState("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [rowError, setRowError] = useState<string | null>(null);
  const showForm = !link || editing;

  const save = async () => {
    if (!url.trim()) return;
    setSaving(true);
    setRowError(null);
    try {
      const res = await fetch(apiUrl("/api/profile/sources/linkedin-link"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json().catch(() => null);
      if (res.status === 404 || res.status === 405) {
        throw new Error("The API server is running an older version. Restart bridge_server.py to save a LinkedIn link.");
      }
      if (!res.ok) throw new Error(data?.detail || "Couldn't save that link.");
      onReplaced(data.source);
      setUrl("");
      setEditing(false);
    } catch (e) {
      setRowError(e instanceof Error ? e.message : "Couldn't save that link.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={row}>
      <div style={rowTitle}>LinkedIn</div>
      <div style={hintText}>Your profile address, saved as a link.</div>
      {showForm ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            save();
          }}
          style={{ display: "flex", gap: 8, marginTop: 8 }}
        >
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="linkedin.com/in/yourname"
            aria-label="LinkedIn profile address"
            style={{ ...input, flex: 1 }}
          />
          <button type="submit" style={btn} disabled={saving || !url.trim()}>
            Save
          </button>
          {editing && (
            <button type="button" style={btn} onClick={() => setEditing(false)}>
              Cancel
            </button>
          )}
        </form>
      ) : (
        <div style={{ position: "relative" }}>
          <SourceItem apiUrl={apiUrl} source={link} onRemove={onRemove} />
          <button
            style={{ ...linkBtn, marginTop: 4 }}
            onClick={() => {
              setUrl(link.url ?? "");
              setEditing(true);
            }}
          >
            Change link
          </button>
        </div>
      )}
      {rowError && <div style={rowErrorText}>{rowError}</div>}

      <div style={{ marginTop: 12 }}>
        <DocumentRow
          apiUrl={apiUrl}
          kind="linkedin"
          title="Add details from LinkedIn (optional)"
          hint="LinkedIn can't be read from a link. If your LinkedIn has things your resume doesn't (older roles, certifications, volunteering), open your profile, choose More → Save to PDF, and upload that file."
          sources={pdfs}
          onAdded={onAdded}
          onRemove={onRemove}
          nested
        />
      </div>
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
      <div style={hintText}>
        Saved as a link. When you press Read it, the page and up to 5 pages it links to on the same site (like About
        or Projects) are read.
      </div>
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
      {sources
        .filter((s) => !s.has_file)
        .map((s) => (
          <SourceItem key={s.id} apiUrl={apiUrl} source={s} onRemove={onRemove} />
        ))}

      <div style={{ marginTop: 12 }}>
        <DocumentRow
          apiUrl={apiUrl}
          kind="website"
          title="Or upload a PDF of your site"
          hint="For sites that can't be read from a link. In your browser, open each page you want included and choose Print → Save as PDF."
          sources={sources.filter((s) => s.has_file)}
          onAdded={onAdded}
          onRemove={onRemove}
          nested
        />
      </div>
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
const consentBox: React.CSSProperties = { marginTop: 10, padding: "14px 16px", border: "1px solid #bfdbfe", background: "#eff6ff", borderRadius: 10 };
const reviewBox: React.CSSProperties = { marginTop: 10, padding: "12px 14px", background: "#fff", border: "1px solid #dbe7f7", borderRadius: 8 };
const proposedRow: React.CSSProperties = { display: "flex", gap: 12, alignItems: "flex-start", padding: "8px 0", borderTop: "1px solid #f3f4f6" };
const quoteText: React.CSSProperties = { fontSize: 12, color: "#6b7280", marginTop: 2, fontStyle: "italic", wordBreak: "break-word" };
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
