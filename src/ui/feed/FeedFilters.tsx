import React from "react";

type FeedFiltersValues = {
  location: string;
  role: string;
  experience: string;
  company: string;
};

type FeedFiltersSetters = {
  setLocationFilter: (value: string) => void;
  setRoleFilter: (value: string) => void;
  setExperienceFilter: (value: string) => void;
  setCompanyFilter: (value: string) => void;
};

type FeedFiltersProps = {
  filters: FeedFiltersValues;
  setFilters: FeedFiltersSetters;
};

export function FeedFilters({ filters, setFilters }: FeedFiltersProps) {
  return (
    <div style={{ padding: 20, flexShrink: 0, position: "sticky", top: 0, backgroundColor: "#fff", zIndex: 1 }}>
      <h2 style={{ fontSize: "18px", marginBottom: "20px" }}>Daily Feed</h2>
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
      </div>
    </div>
  );
}
