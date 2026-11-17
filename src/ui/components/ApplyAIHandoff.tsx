import React, { useEffect, useState } from "react";

/**
 * "Explore in applyAI" — user-initiated, one-way role handoff.
 * Contract: docs/APPLYAI_HANDOFF_CONTRACT.md (§2 preconditions, §4 sending rules).
 *
 * - Renders nothing unless VITE_APPLYAI_HANDOFF_URL names a destination (§8).
 * - Fetches the envelope from the read-only /api/applyai-envelope endpoint.
 * - Shows exactly what will be sent and waits for an explicit confirm.
 * - Sends by browser form POST in a new tab; no backend call, no state change here.
 */

const HANDOFF_URL = (import.meta.env.VITE_APPLYAI_HANDOFF_URL ?? "").trim();

type Envelope = {
  handoff_version: string;
  source: {
    company: string;
    title: string;
    job_url: string;
    interpreted_at: string;
  };
  role: {
    summary_text: string;
    explicit_requirements: { requirement_text: string; modality: string }[];
    capability_emphasis: { domain_label: string; description: string; evidence: string[] }[];
    project_opportunities: { capability_surface: string; description: string; evidence: string[] }[];
    structural_notes: string;
    confidence: string;
  };
  framing: string;
};

function newHandoffId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
}

function sendViaForm(url: string, envelope: Envelope) {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = url;
  form.target = "_blank";
  form.rel = "noopener noreferrer";
  form.style.display = "none";

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = "envelope";
  input.value = JSON.stringify({ ...envelope, handoff_id: newHandoffId() });
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit();
  form.remove();
}

export function ApplyAIHandoff({
  jobId,
  apiUrl,
}: {
  jobId: string;
  apiUrl: (path: string) => string;
}) {
  const [envelope, setEnvelope] = useState<Envelope | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    setEnvelope(null);
    setError(null);
    setLoading(false);
    setSent(false);
  }, [jobId]);

  useEffect(() => {
    if (!envelope) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setEnvelope(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [envelope]);

  if (!HANDOFF_URL) return null;

  const openPreview = async () => {
    setLoading(true);
    setError(null);
    setSent(false);
    try {
      const res = await fetch(apiUrl(`/api/applyai-envelope?job_id=${encodeURIComponent(jobId)}`));
      const data = await res.json().catch(() => null);
      if (!res.ok || !data?.envelope) {
        setError(data?.detail ?? "Couldn't prepare this role for applyAI.");
        return;
      }
      setEnvelope(data.envelope);
    } catch {
      setError("Couldn't reach the letsA(ppl)I server.");
    } finally {
      setLoading(false);
    }
  };

  const confirmSend = () => {
    if (!envelope) return;
    sendViaForm(HANDOFF_URL, envelope);
    setEnvelope(null);
    setSent(true);
  };

  return (
    <div style={{ marginTop: "8px", padding: "16px 0", borderTop: "1px solid #e5e7eb" }}>
      <button onClick={openPreview} disabled={loading} style={secondaryButton}>
        {loading ? "Preparing…" : "Explore in applyAI…"}
      </button>
      <span style={{ marginLeft: "10px", fontSize: "13px", color: "#666" }}>
        Opens a preview first. Nothing is sent until you confirm.
      </span>
      {error && <p style={{ color: "#b42318", fontSize: "13px", margin: "8px 0 0" }}>{error}</p>}
      {sent && (
        <p style={{ color: "#555", fontSize: "13px", margin: "8px 0 0" }}>
          Sent to applyAI in a new tab. Confirm it there to start exploring.
        </p>
      )}

      {envelope && (
        <div role="dialog" aria-modal="true" aria-labelledby="applyai-preview-title" style={overlay}>
          <div style={dialog}>
            <h2 id="applyai-preview-title" style={{ marginTop: 0, fontSize: "18px" }}>
              Send this role to applyAI?
            </h2>
            <p style={{ fontWeight: 600, margin: "0 0 12px" }}>{envelope.framing}</p>

            <div style={section}>
              <div style={label}>What will be sent</div>
              <div style={{ fontWeight: 600 }}>
                {envelope.source.title} · {envelope.source.company}
              </div>
              <p style={{ margin: "6px 0" }}>{envelope.role.summary_text}</p>
              <ul style={{ margin: "6px 0", paddingLeft: "18px", fontSize: "14px" }}>
                <li>{envelope.role.explicit_requirements.length} listed requirements</li>
                <li>
                  Capabilities:{" "}
                  {envelope.role.capability_emphasis.map((c) => c.domain_label).join(", ")}
                </li>
                <li>
                  Project ideas:{" "}
                  {envelope.role.project_opportunities.length > 0
                    ? envelope.role.project_opportunities.map((p) => p.capability_surface).join(", ")
                    : "none"}
                </li>
                <li>Quoted lines from the posting as evidence, and a link to it</li>
              </ul>
            </div>

            <div style={section}>
              <div style={label}>What is not sent</div>
              <p style={{ margin: 0, fontSize: "14px" }}>
                Your pipeline status, stars, notes, resume, or anything else about you.
              </p>
            </div>

            <p style={{ fontSize: "13px", color: "#555" }}>
              Once sent, letsA(ppl)I can't update or withdraw it, even if you revoke
              interpretation here. You can clear it inside applyAI at any time.
            </p>

            <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
              <button onClick={() => setEnvelope(null)} style={secondaryButton}>
                Cancel
              </button>
              <button onClick={confirmSend} style={primaryButton}>
                Send to applyAI
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const overlay: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(17, 24, 39, 0.45)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
  padding: "16px",
};

const dialog: React.CSSProperties = {
  background: "#fff",
  borderRadius: "12px",
  padding: "24px",
  maxWidth: "560px",
  width: "100%",
  maxHeight: "85vh",
  overflowY: "auto",
  boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
};

const section: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: "8px",
  padding: "12px",
  marginBottom: "12px",
};

const label: React.CSSProperties = {
  fontSize: "11px",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  color: "#666",
  marginBottom: "6px",
};

const secondaryButton: React.CSSProperties = {
  padding: "8px 14px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  background: "#fff",
  cursor: "pointer",
  fontSize: "14px",
};

const primaryButton: React.CSSProperties = {
  ...secondaryButton,
  background: "#111827",
  color: "#fff",
  border: "1px solid #111827",
};
