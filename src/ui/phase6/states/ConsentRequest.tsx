import React from "react";

interface ConsentRequestProps {
  title: string;
  description: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConsentRequest({
  title,
  description,
  onConfirm,
  onCancel,
}: ConsentRequestProps) {
  return (
    <div style={{ padding: "16px", lineHeight: 1.5 }}>
      <h3>{title}</h3>

      <p>{description}</p>

      <div style={{ marginTop: "16px" }}>
        <button
          onClick={onConfirm}
          style={{ marginRight: "12px" }}
        >
          Confirm
        </button>

        <button onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}