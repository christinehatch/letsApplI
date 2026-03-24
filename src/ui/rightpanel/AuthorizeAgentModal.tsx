import React from "react";

type AuthorizationStatus = "idle" | "authorizing" | "executing";

interface AuthorizeAgentModalProps {
  open: boolean;
  status: AuthorizationStatus;
  onCancel: () => void;
  onAuthorize: () => void;
}

export function AuthorizeAgentModal({
  open,
  status,
  onCancel,
  onAuthorize,
}: AuthorizeAgentModalProps) {
  if (!open) return null;

  const isWorking = status === "authorizing" || status === "executing";

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15, 23, 42, 0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 2000,
        padding: "16px",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "#fff",
          borderRadius: "12px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
          overflow: "hidden",
        }}
      >
        <div style={{ padding: "16px", borderBottom: "1px solid #eee" }}>
          <div style={{ fontSize: "16px", fontWeight: 700, color: "#111827" }}>
            Authorize letsA(ppl)I Agent
          </div>
          <div style={{ marginTop: "8px", fontSize: "14px", color: "#4b5563", lineHeight: 1.5 }}>
            You are authorizing the agent to submit this application on your behalf using
            prepared responses.
          </div>
        </div>

        <div style={{ padding: "16px", borderBottom: "1px solid #eee" }}>
          <div style={{ fontSize: "12px", color: "#6b7280", fontWeight: 700, marginBottom: "6px" }}>
            Scope
          </div>
          <div
            style={{
              display: "inline-block",
              padding: "6px 10px",
              borderRadius: "999px",
              border: "1px solid #d1d5db",
              fontSize: "12px",
              fontWeight: 600,
              color: "#1f2937",
              background: "#f9fafb",
            }}
          >
            apply:job
          </div>
        </div>

        <div style={{ padding: "16px", display: "flex", justifyContent: "flex-end", gap: "8px" }}>
          <button
            type="button"
            onClick={onCancel}
            disabled={isWorking}
            style={{
              padding: "10px 14px",
              borderRadius: "8px",
              border: "1px solid #ddd",
              background: "#fff",
              color: "#111827",
              fontWeight: 600,
              cursor: isWorking ? "not-allowed" : "pointer",
              opacity: isWorking ? 0.6 : 1,
            }}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onAuthorize}
            disabled={isWorking}
            style={{
              padding: "10px 14px",
              borderRadius: "8px",
              border: "1px solid #ddd",
              background: "#fff",
              color: "#111827",
              fontWeight: 600,
              cursor: isWorking ? "not-allowed" : "pointer",
              opacity: isWorking ? 0.6 : 1,
            }}
          >
            {status === "authorizing"
              ? "Authorizing..."
              : status === "executing"
              ? "Executing..."
              : "Authorize"}
          </button>
        </div>
      </div>
    </div>
  );
}
