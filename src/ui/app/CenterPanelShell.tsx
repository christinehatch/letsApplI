import React from "react";

type CenterPanelShellProps = {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  context?: React.ReactNode;
  children: React.ReactNode;
};

export function CenterPanelShell({
  title,
  subtitle,
  actions,
  context,
  children,
}: CenterPanelShellProps) {
  return (
    <section style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div
        style={{
          position: "sticky",
          top: 0,
          zIndex: 20,
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          padding: "16px",
          boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "16px" }}>
          <div style={{ minWidth: 0 }}>
            <h1 style={{ margin: 0, fontSize: "24px", color: "#111827" }}>{title}</h1>
            {subtitle && <p style={{ margin: "8px 0 0 0", color: "#666", fontSize: "13px" }}>{subtitle}</p>}
          </div>
          {actions && <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>{actions}</div>}
        </div>
        {context && <div style={{ marginTop: "12px" }}>{context}</div>}
      </div>
      <div>{children}</div>
    </section>
  );
}
