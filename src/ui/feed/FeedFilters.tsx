import React from "react";

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
  showChrome?: boolean;
};

export function FeedFilters({
  filters,
  setFilters,
  viewMode,
  setViewMode,
  showChrome = true,
}: FeedFiltersProps) {
  const activeFilterChips: Array<{ key: string; label: string; onRemove: () => void }> = [];
  if (filters.location.trim()) {
    activeFilterChips.push({
      key: `location:${filters.location}`,
      label: `Location: ${filters.location}`,
      onRemove: () => setFilters.setLocationFilter(""),
    });
  }
  if (filters.role.trim()) {
    activeFilterChips.push({
      key: `role:${filters.role}`,
      label: `Role: ${filters.role}`,
      onRemove: () => setFilters.setRoleFilter(""),
    });
  }
  if (filters.experience.trim()) {
    activeFilterChips.push({
      key: `experience:${filters.experience}`,
      label: `Experience: ${filters.experience}`,
      onRemove: () => setFilters.setExperienceFilter(""),
    });
  }
  if (filters.company.trim()) {
    activeFilterChips.push({
      key: `company:${filters.company}`,
      label: `Company: ${filters.company}`,
      onRemove: () => setFilters.setCompanyFilter(""),
    });
  }
  for (const signal of filters.signals) {
    activeFilterChips.push({
      key: `signal:${signal}`,
      label: `Signal: ${signal}`,
      onRemove: () => setFilters.setSignalsFilter(filters.signals.filter((s) => s !== signal)),
    });
  }
  if (filters.aiOnly) {
    activeFilterChips.push({
      key: "aiOnly",
      label: "AI only",
      onRemove: () => setFilters.setAiOnly(false),
    });
  }

  return (
    <div
      style={{
        padding: showChrome ? "16px" : "0 16px 16px 16px",
        flexShrink: 0,
        position: showChrome ? "sticky" : "static",
        top: showChrome ? 0 : undefined,
        backgroundColor: "#fff",
        zIndex: 1,
      }}
    >
      {showChrome && (
        <>
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
        </>
      )}
      {viewMode === "feed" && (
        <div style={{ display: "grid", gap: "8px", marginBottom: "16px" }}>
          <input
            placeholder="Location"
            value={filters.location}
            onChange={(e) => setFilters.setLocationFilter(e.target.value)}
            style={{ padding: "8px 12px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <input
            placeholder="Role keyword"
            value={filters.role}
            onChange={(e) => setFilters.setRoleFilter(e.target.value)}
            style={{ padding: "8px 12px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <select
            value={filters.experience}
            onChange={(e) => setFilters.setExperienceFilter(e.target.value)}
            style={{ padding: "8px 12px", border: "1px solid #ddd", borderRadius: "8px" }}
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
            style={{ padding: "8px 12px", border: "1px solid #ddd", borderRadius: "8px" }}
          />
          <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px", color: "#333" }}>
            <input
              type="checkbox"
              checked={filters.aiOnly}
              onChange={(e) => setFilters.setAiOnly(e.target.checked)}
            />
            AI roles only
          </label>
          {activeFilterChips.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {activeFilterChips.map((chip) => (
                <span
                  key={chip.key}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    fontSize: "12px",
                    color: "#4b5563",
                    background: "#f3f4f6",
                    border: "1px solid #e5e7eb",
                    borderRadius: "999px",
                    padding: "4px 8px",
                  }}
                >
                  {chip.label}
                  <button
                    type="button"
                    onClick={chip.onRemove}
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#6b7280",
                      cursor: "pointer",
                      fontSize: "12px",
                      padding: 0,
                      lineHeight: 1,
                    }}
                    aria-label={`Remove ${chip.label} filter`}
                    title={`Remove ${chip.label} filter`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
