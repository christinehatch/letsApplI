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

  const tabStyle = (active: boolean): React.CSSProperties => ({
    flex: 1,
    padding: "10px 12px",
    border: "none",
    borderBottom: active ? "2px solid #0070f3" : "2px solid transparent",
    background: "none",
    fontWeight: active ? 600 : 400,
    cursor: "pointer",
    color: active ? "#0070f3" : "#555"
  });

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", padding: "12px 12px 0 12px", background: "#fafafa" }}>
        <button
          type="button"
          style={tabStyle(activeTab === "phase")}
          onClick={() => setActiveTab("phase")}
        >
          Phase
        </button>
        <button
          type="button"
          style={tabStyle(activeTab === "chat")}
          onClick={() => setActiveTab("chat")}
        >
          Chat
        </button>
        <button
          type="button"
          style={tabStyle(activeTab === "notes")}
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
