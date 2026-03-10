import React, { useState } from "react";

type FeedFiltersValues = {
  location: string;
  role: string;
  experience: string;
  company: string;
  signals: string[];
  aiOnly: boolean;
};

type FeedFiltersSetters = {
  setLocationFilter: (value: string) => void;
  setRoleFilter: (value: string) => void;
  setExperienceFilter: (value: string) => void;
  setCompanyFilter: (value: string) => void;
  setSignalsFilter: (value: string[]) => void;
  setAiOnly: (value: boolean) => void;
};

type FeedFiltersProps = {
  filters: FeedFiltersValues;
  setFilters: FeedFiltersSetters;
  viewMode: "feed" | "saved";
  setViewMode: (mode: "feed" | "saved") => void;
};

export function FeedFilters({ filters, setFilters, viewMode, setViewMode }: FeedFiltersProps) {
  const [filtersExpanded, setFiltersExpanded] = useState(false);
  const domains = [
    "engineering",
    "ai_ml",
    "data",
    "product",
    "security",
    "infrastructure",
  ];

  const toggleDomain = (domain: string) => {
    if (filters.signals.includes(domain)) {
      setFilters.setSignalsFilter(filters.signals.filter((d) => d !== domain));
      return;
    }
    setFilters.setSignalsFilter([...filters.signals, domain]);
  };

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
          <button
            onClick={() => setFiltersExpanded(!filtersExpanded)}
            style={{
              marginTop: "8px",
              padding: "6px 10px",
              borderRadius: "6px",
              border: "1px solid #ddd",
              background: "#fff",
              cursor: "pointer",
            }}
          >
            Filters {filtersExpanded ? "▾" : "▸"}
          </button>
          {filtersExpanded && (
            <div style={{ marginTop: "10px" }}>
              <div style={{ fontWeight: 600, marginBottom: "6px" }}>
                Domains
              </div>
              {domains.map((domain) => (
                <label key={domain} style={{ display: "block", marginBottom: "4px" }}>
                  <input
                    type="checkbox"
                    checked={filters.signals.includes(domain)}
                    onChange={() => toggleDomain(domain)}
                  />
                  {" "}
                  {domain.replace("_", " ").toUpperCase()}
                </label>
              ))}
            </div>
          )}
          <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "#333" }}>
            <input
              type="checkbox"
              checked={filters.aiOnly}
              onChange={(e) => setFilters.setAiOnly(e.target.checked)}
            />
            AI roles only
          </label>
        </div>
      )}
    </div>
  );
}
