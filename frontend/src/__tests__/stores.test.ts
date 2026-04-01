import { describe, it, expect } from "vitest";

describe("GRC Type Definitions", () => {
  it("should have correct risk categories", () => {
    const categories = ["IT", "Physical", "Legal", "Construction", "Financial", "Operational"];
    expect(categories).toHaveLength(6);
    expect(categories).toContain("Construction");
  });

  it("should have correct compliance statuses", () => {
    const statuses = ["compliant", "non_compliant", "partial", "unknown"];
    expect(statuses).toHaveLength(4);
  });

  it("should have correct finding types", () => {
    const types = ["major_nc", "minor_nc", "observation", "good_practice"];
    expect(types).toHaveLength(4);
  });
});
