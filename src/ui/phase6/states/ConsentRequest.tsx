import React from "react";

interface ConsentRequestProps {
  title: string;
  description: string;
  primaryActionButtonStyle: React.CSSProperties;
  secondaryActionButtonStyle: React.CSSProperties;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConsentRequest({
  title,
  description,
  primaryActionButtonStyle,
  secondaryActionButtonStyle,
  onConfirm,
  onCancel,
}: ConsentRequestProps) {
  return (
    <div style={{ padding: "16px", lineHeight: 1.5 }}>
      <h3>{title}</h3>

      <p>{description}</p>

      <div style={{ marginTop: "16px", display: "flex", gap: "8px" }}>
        <button
          onClick={onConfirm}
          style={{ ...primaryActionButtonStyle, flex: 1 }}
        >
          Confirm
        </button>

        <button
          onClick={onCancel}
          style={{ ...secondaryActionButtonStyle, flex: 1 }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
