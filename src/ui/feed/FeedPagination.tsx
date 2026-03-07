import React from "react";

type FeedPaginationProps = {
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
};

export function FeedPagination({ page, setPage, totalPages }: FeedPaginationProps) {
  return (
    <div style={{ borderTop: "1px solid #eee", padding: "12px 20px", backgroundColor: "#fff", flexShrink: 0 }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
          style={{
            padding: "8px 10px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            background: page <= 1 ? "#f5f5f5" : "#fff",
            cursor: page <= 1 ? "not-allowed" : "pointer",
          }}
        >
          Previous
        </button>
        <div style={{ fontSize: "12px", color: "#555" }}>
          Page {page} of {totalPages}
        </div>
        <button
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages}
          style={{
            padding: "8px 10px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            background: page >= totalPages ? "#f5f5f5" : "#fff",
            cursor: page >= totalPages ? "not-allowed" : "pointer",
          }}
        >
          Next
        </button>
      </div>
    </div>
  );
}
