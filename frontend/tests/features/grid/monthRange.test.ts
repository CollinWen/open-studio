/**
 * Tests for monthRange: every month from first to last entry (gaps counted
 * as zero, across a new year), how a month reads, and range edges.
 */

import { describe, expect, it } from "vitest";
import { countMonths, formatMonth, isInRange } from "../../../src/features/grid/monthRange";
import { makeEntry } from "../../makeEntry";

describe("countMonths", () => {
  it("counts every month from first to last, gaps included", () => {
    const entries = ["2023-11-02", "2024-02-20", "2023-11-30"].map((day) => makeEntry({ occurred_at: day }));
    expect(countMonths(entries)).toEqual([
      { month: "2023-11", count: 2 },
      { month: "2023-12", count: 0 },
      { month: "2024-01", count: 0 },
      { month: "2024-02", count: 1 },
    ]);
  });

  it("is empty with no entries", () => {
    expect(countMonths([])).toEqual([]);
  });
});

describe("formatMonth and isInRange", () => {
  it("reads a month as a short name and year", () => {
    expect(formatMonth("2024-03")).toBe("Mar 2024");
  });

  it("includes both ends of a range", () => {
    const range = { from: "2023-04", to: "2024-09" };
    expect(isInRange("2023-04", range)).toBe(true);
    expect(isInRange("2024-09", range)).toBe(true);
    expect(isInRange("2024-10", range)).toBe(false);
  });
});
