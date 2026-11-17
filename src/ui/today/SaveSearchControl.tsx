import React, { useEffect, useState } from "react";

/**
 * "Save this search" for the Search sidebar. Saved searches feed the Today view.
 */
export function SaveSearchControl({
  apiUrl,
  role,
  location,
  company,
  onOpenToday,
}: {
  apiUrl: (path: string) => string;
  role: string;
  location: string;
  company: string;
  onOpenToday: () => void;
}) {
  const hasSearch = [role, location, company].some((v) => v.trim().length > 0);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [includeExisting, setIncludeExisting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setOpen(false);
    setSaved(null);
    setError(null);
  }, [role, location, company]);

  if (!hasSearch) return null;

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(apiUrl("/api/saved-searches"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: role.trim(),
          location: location.trim(),
          company: company.trim(),
          name: name.trim() || undefined,
          include_existing: includeExisting,
        }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.detail || "Couldn't save this search.");
      setSaved(data.search.name);
      setOpen(false);
      setName("");
      setIncludeExisting(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't save this search.");
    } finally {
      setSaving(false);
    }
  };

  if (saved) {
    return (
      <div style={{ fontSize: 13, color: "#374151" }}>
        Saved “{saved}”.{" "}
        <button type="button" onClick={onOpenToday} style={link}>Open Today</button>
      </div>
    );
  }

  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} style={button}>
        Save this search
      </button>
    );
  }

  return (
    <div style={{ display: "grid", gap: 8, border: "1px solid #e5e7eb", borderRadius: 10, padding: 10 }}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name (optional)"
        style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #d1d5db", fontSize: 14 }}
      />
      <label style={{ display: "flex", gap: 8, fontSize: 13, color: "#374151", alignItems: "flex-start" }}>
        <input type="checkbox" checked={includeExisting} onChange={(e) => setIncludeExisting(e.target.checked)} />
        <span>
          Also include roles that are already open
          <span style={{ display: "block", color: "#6b7280" }}>
            Otherwise Today only shows roles found from now on.
          </span>
        </span>
      </label>
      {error && <div style={{ color: "#b42318", fontSize: 13 }}>{error}</div>}
      <div style={{ display: "flex", gap: 8 }}>
        <button type="button" onClick={save} disabled={saving} style={{ ...button, background: "#111827", color: "#fff", borderColor: "#111827" }}>
          {saving ? "Saving…" : "Save"}
        </button>
        <button type="button" onClick={() => setOpen(false)} style={button}>Cancel</button>
      </div>
    </div>
  );
}

const button: React.CSSProperties = {
  padding: "7px 12px",
  borderRadius: 8,
  border: "1px solid #d1d5db",
  background: "#fff",
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
  justifySelf: "start",
};

const link: React.CSSProperties = { border: "none", background: "transparent", color: "#185fa5", cursor: "pointer", padding: 0, fontSize: 13 };
