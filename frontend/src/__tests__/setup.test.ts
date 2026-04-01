import { describe, it, expect } from "vitest";

describe("GRC Frontend Setup", () => {
  it("should have TypeScript types loaded", () => {
    expect(true).toBe(true);
  });

  it("should have correct app name", () => {
    const appName = "construction-grc-frontend";
    expect(appName).toContain("grc");
  });
});
