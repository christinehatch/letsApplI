import React from "react";

type FeedFiltersValues = {
  location: string;
  role: string;
  experience: string;
  company: string;
  aiFilter: string;
};

type FeedFiltersSetters = {
  setLocationFilter: (value: string) => void;
  setRoleFilter: (value: string) => void;
  setExperienceFilter: (value: string) => void;
  setCompanyFilter: (value: string) => void;
  setAiFilter: (value: string) => void;
};

type FeedFiltersProps = {
  filters: FeedFiltersValues;
  setFilters: FeedFiltersSetters;
  viewMode: "feed" | "saved";
  setViewMode: (mode: "feed" | "saved") => void;
};

export function FeedFilters({ filters, setFilters, viewMode, setViewMode }: FeedFiltersProps) {
  return (
    <div style={{ padding: 20, flexShrink: 0, position: "sticky", top: 0, backgroundColor: "#fff", zIndex: 1 }}>
      <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
        <button
          onClick={() => setViewMode("feed")}
          style={{
            border: "1px solid #ddd",
            background: viewMode === "feed" ? "#f0f7ff" : "#fff",
            borderRadius: "8px",
            padding: "8px 10px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Daily Feed
        </button>
        <button
          onClick={() => setViewMode("saved")}
          style={{
            border: "1px solid #ddd",
            background: viewMode === "saved" ? "#f0f7ff" : "#fff",
            borderRadius: "8px",
            padding: "8px 10px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Saved Jobs
        </button>
      </div>
      <h2 style={{ fontSize: "18px", marginBottom: "16px" }}>
        {viewMode === "feed" ? "Daily Feed" : "Saved Jobs"}
      </h2>
      {viewMode === "feed" && (
        <div style={{ display: "grid", gap: "8px", marginBottom: "16px" }}>
          <input
            placeholder="Location"
            value={filters.location}
            onChange={(e) => setFilters.setLocationFilter(e.target.value)}
            style={{ padding: "8px 10px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <input
            placeholder="Role keyword"
            value={filters.role}
            onChange={(e) => setFilters.setRoleFilter(e.target.value)}
            style={{ padding: "8px 10px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <select
            value={filters.experience}
            onChange={(e) => setFilters.setExperienceFilter(e.target.value)}
            style={{ padding: "8px 10px", border: "1px solid #ddd", borderRadius: "8px" }}
          >
            <option value="">All experience</option>
            <option value="junior">Junior</option>
            <option value="mid">Mid</option>
            <option value="senior">Senior</option>
          </select>
          <input
            placeholder="Company"
            value={filters.company}
            onChange={(e) => setFilters.setCompanyFilter(e.target.value)}
            style={{ padding: "8px 10px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <select
            value={filters.aiFilter}
            onChange={(e) => setFilters.setAiFilter(e.target.value)}
            style={{ padding: "8px 10px", border: "1px solid #ddd", borderRadius: "8px" }}
          >
            <option value="">All jobs</option>
            <option value="ai_only">AI-only jobs</option>
          </select>
        </div>
      )}
    </div>
  );
}
