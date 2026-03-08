import React, {
  forwardRef,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import {
  Phase6SidePanel,
  type Phase6SidePanelHandle,
  type Phase6SidePanelProps,
} from "../phase6/Phase6SidePanel";

type RightPanelTab = "phase" | "chat" | "notes";

export const RightPanel = forwardRef<
  Phase6SidePanelHandle,
  Phase6SidePanelProps
>(function RightPanel(props, ref) {
  const [activeTab, setActiveTab] = useState<RightPanelTab>("phase");
  const phaseRef = useRef<Phase6SidePanelHandle | null>(null);

  useImperativeHandle(
    ref,
    () => ({
      requestInterpretation: () => {
        phaseRef.current?.requestInterpretation();
      },
      completeInterpretation: () => {
        phaseRef.current?.completeInterpretation();
      },
      restoreInterpreted: (interpretation: unknown) => {
        phaseRef.current?.restoreInterpreted(interpretation);
      },
      reset: () => {
        phaseRef.current?.reset();
      },
      revoke: () => {
        phaseRef.current?.revoke();
      },
    }),
    []
  );

  const tabButtonStyle = (active: boolean): React.CSSProperties => ({
    padding: "8px 10px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    background: active ? "#f5f5f5" : "#fff",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "13px",
  });

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", gap: "8px", padding: "12px 12px 0 12px" }}>
        <button
          type="button"
          style={tabButtonStyle(activeTab === "phase")}
          onClick={() => setActiveTab("phase")}
        >
          Phase
        </button>
        <button
          type="button"
          style={tabButtonStyle(activeTab === "chat")}
          onClick={() => setActiveTab("chat")}
        >
          Chat
        </button>
        <button
          type="button"
          style={tabButtonStyle(activeTab === "notes")}
          onClick={() => setActiveTab("notes")}
        >
          Notes
        </button>
      </div>

      <div style={{ flex: 1, overflow: "auto" }}>
        {activeTab === "phase" && <Phase6SidePanel ref={phaseRef} {...props} />}
        {activeTab === "chat" && (
          <div style={{ padding: "16px", color: "#666" }}>Chat coming soon</div>
        )}
        {activeTab === "notes" && (
          <div style={{ padding: "16px", color: "#666" }}>Notes coming soon</div>
        )}
      </div>
    </div>
  );
});

RightPanel.displayName = "RightPanel";
