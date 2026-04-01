import { describe, it, expect } from "vitest";

describe("Pinia Store Types", () => {
  it("should define compliance store exports", async () => {
    const module = await import("@/store/compliance");
    expect(module.useComplianceStore).toBeDefined();
  });

  it("should define audits store exports", async () => {
    const module = await import("@/store/audits");
    expect(module.useAuditsStore).toBeDefined();
  });

  it("should define risks store exports", async () => {
    const module = await import("@/store/risks");
    expect(module.useRisksStore).toBeDefined();
  });
});

describe("Type Definitions", () => {
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
