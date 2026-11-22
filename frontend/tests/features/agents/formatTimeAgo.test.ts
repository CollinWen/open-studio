/**
 * Tests for formatTimeAgo: plain words for recent times, a date after a
 * week, and server times without a zone read as UTC.
 */

import { describe, expect, it } from "vitest";
import { formatTimeAgo } from "../../../src/features/agents/formatTimeAgo";

const NOW = Date.parse("2026-11-20T12:00:00Z");
const ago = (milliseconds: number) => new Date(NOW - milliseconds).toISOString();
const MINUTE = 60_000;

describe("formatTimeAgo", () => {
  it("uses plain words for recent times", () => {
    expect(formatTimeAgo(ago(20_000), NOW)).toBe("just now");
    expect(formatTimeAgo(ago(12 * MINUTE), NOW)).toBe("12 min ago");
    expect(formatTimeAgo(ago(3 * 60 * MINUTE), NOW)).toBe("3 h ago");
    expect(formatTimeAgo(ago(30 * 60 * MINUTE), NOW)).toBe("1 day ago");
    expect(formatTimeAgo(ago(3 * 24 * 60 * MINUTE), NOW)).toBe("3 days ago");
  });

  it("gives the date once it's more than a week old", () => {
    expect(formatTimeAgo("2026-10-01T12:00:00Z", NOW)).toBe("Oct 1, 2026");
  });

  it("reads a time without a zone as UTC", () => {
    expect(formatTimeAgo("2026-11-20T11:50:00", NOW)).toBe("10 min ago");
  });
});
