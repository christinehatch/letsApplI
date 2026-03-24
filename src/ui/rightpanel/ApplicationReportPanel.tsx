import React from "react";
import { AuthorizeAgentModal } from "./AuthorizeAgentModal";
import { useAuth0 } from "@auth0/auth0-react";

export interface ApplicationPreparationResult {
  cover_letter: string;
  answers: {
    why_this_role: string;
    relevant_experience: string;
    strengths: string;
  };
  resume_highlights: string[];
}

interface ApplicationReportPanelProps {
  loading: boolean;
  application: ApplicationPreparationResult | null;
}

type ApplyFlowStatus = "idle" | "authorizing" | "executing" | "success";
const AGENT_APPLY_PENDING_KEY = "agent_apply_pending";

const sectionTitleStyle: React.CSSProperties = {
  margin: "0 0 6px 0",
  fontSize: "13px",
  color: "#4b5563",
  fontWeight: 700,
};

const sectionBodyStyle: React.CSSProperties = {
  margin: 0,
  fontSize: "14px",
  color: "#111827",
  lineHeight: 1.5,
};

export function ApplicationReportPanel({
  loading,
  application,
}: ApplicationReportPanelProps) {
  const { isAuthenticated, loginWithRedirect, user } = useAuth0();
  const [modalOpen, setModalOpen] = React.useState(false);
  const [applyFlowStatus, setApplyFlowStatus] = React.useState<ApplyFlowStatus>("idle");
  const [confirmationId, setConfirmationId] = React.useState<string | null>(null);

  const runExecutionFlow = React.useCallback(async () => {
    setApplyFlowStatus("authorizing");
    await new Promise((r) => setTimeout(r, 800));
    setApplyFlowStatus("executing");
    await new Promise((r) => setTimeout(r, 1000));
    setApplyFlowStatus("success");
    setModalOpen(false);
    setConfirmationId(`AGT-${Date.now().toString().slice(-8)}`);
  }, []);

  const handleOpenModal = () => {
    setModalOpen(true);
  };

  const handleCancelModal = () => {
    if (applyFlowStatus === "authorizing" || applyFlowStatus === "executing") {
      return;
    }
    setModalOpen(false);
  };

  const handleAuthorize = async () => {
    if (!isAuthenticated) {
      sessionStorage.setItem(AGENT_APPLY_PENDING_KEY, "1");
      await loginWithRedirect();
      return;
    }

    await runExecutionFlow();
  };

  React.useEffect(() => {
    if (!isAuthenticated) return;
    if (sessionStorage.getItem(AGENT_APPLY_PENDING_KEY) !== "1") return;
    sessionStorage.removeItem(AGENT_APPLY_PENDING_KEY);
    void runExecutionFlow();
  }, [isAuthenticated, runExecutionFlow]);

  const showSubmittedView = applyFlowStatus === "success" && confirmationId;

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ padding: "16px", borderBottom: "1px solid #eee", background: "#fafafa" }}>
        <div style={{ fontWeight: 700, color: "#111827" }}>Application Report</div>
        <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
          Drafted responses from the selected role context.
        </div>
        {user?.email && (
          <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "6px" }}>
            {user.email}
          </div>
        )}
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "16px", display: "grid", gap: "16px" }}>
        {showSubmittedView && (
          <div style={{ display: "grid", gap: "16px" }}>
            <section>
              <h3 style={{ margin: 0, fontSize: "18px", color: "#111827" }}>Application Submitted</h3>
              <p style={{ margin: "8px 0 0 0", fontSize: "14px", color: "#4b5563" }}>
                Your agent submission completed successfully.
              </p>
            </section>

            <section
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: "10px",
                padding: "12px",
                background: "#fff",
              }}
            >
              <div style={{ fontSize: "12px", color: "#6b7280", fontWeight: 700, marginBottom: "6px" }}>
                Confirmation ID
              </div>
              <div style={{ fontSize: "14px", color: "#111827", fontWeight: 600 }}>{confirmationId}</div>
            </section>

            <section
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: "10px",
                padding: "12px",
                background: "#fff",
              }}
            >
              <div style={{ fontSize: "14px", color: "#111827", fontWeight: 700, marginBottom: "8px" }}>
                View Agent Details
              </div>
              <div style={{ fontSize: "13px", color: "#4b5563", lineHeight: 1.5 }}>
                Action scope: <strong>apply:job</strong>
                <br />
                Execution mode: simulated frontend flow
              </div>
            </section>
          </div>
        )}

        {!showSubmittedView && (
          <>
        {loading && <div style={{ color: "#666", fontSize: "14px" }}>Generating application...</div>}

        {!loading && !application && (
          <div style={{ color: "#666", fontSize: "14px" }}>
            Application data is not available yet.
          </div>
        )}

        {!loading && application && (
          <>
            <section>
              <h3 style={sectionTitleStyle}>Cover Letter</h3>
              <p style={sectionBodyStyle}>{application.cover_letter}</p>
            </section>

            <section>
              <h3 style={sectionTitleStyle}>Why This Role</h3>
              <p style={sectionBodyStyle}>{application.answers.why_this_role}</p>
            </section>

            <section>
              <h3 style={sectionTitleStyle}>Relevant Experience</h3>
              <p style={sectionBodyStyle}>{application.answers.relevant_experience}</p>
            </section>

            <section>
              <h3 style={sectionTitleStyle}>Strengths</h3>
              <p style={sectionBodyStyle}>{application.answers.strengths}</p>
            </section>

            <section>
              <h3 style={sectionTitleStyle}>Resume Highlights</h3>
              <ul style={{ margin: 0, paddingLeft: "18px", color: "#111827", fontSize: "14px", lineHeight: 1.5 }}>
                {application.resume_highlights.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
          </>
        )}
          </>
        )}
      </div>

      <div style={{ padding: "16px", borderTop: "1px solid #eee", background: "#fff" }}>
        <button
          type="button"
          onClick={handleOpenModal}
          disabled={loading || !application || applyFlowStatus === "success"}
          style={{
            width: "100%",
            padding: "10px 14px",
            borderRadius: "8px",
            border: "1px solid #ddd",
            background: "#fff",
            color: "#111827",
            fontWeight: 600,
            cursor: loading || !application || applyFlowStatus === "success" ? "not-allowed" : "pointer",
            opacity: loading || !application || applyFlowStatus === "success" ? 0.6 : 1,
          }}
        >
          {applyFlowStatus === "success" ? "Application Submitted" : "Apply with Agent"}
        </button>
      </div>

      <AuthorizeAgentModal
        open={modalOpen}
        status={applyFlowStatus === "idle" || applyFlowStatus === "success" ? "idle" : applyFlowStatus}
        onCancel={handleCancelModal}
        onAuthorize={handleAuthorize}
      />
    </div>
  );
}
