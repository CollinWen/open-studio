/**
 * Tests for entryHighlight: nothing fades with nothing picked; an entry
 * fades unless it matches both the picked tag and the picked months.
 */

import { describe, expect, it } from "vitest";
import { isFaded } from "../../../src/features/grid/entryHighlight";
import { makeEntry } from "../../makeEntry";

const bread = makeEntry({ tags: ["bread"], occurred_at: "2024-03-10" });
const spring2024 = { from: "2024-03", to: "2024-05" };

describe("isFaded", () => {
  it("fades nothing when nothing is picked", () => {
    expect(isFaded(bread, { tag: null, range: null })).toBe(false);
  });

  it("fades an entry without the picked tag", () => {
    expect(isFaded(bread, { tag: "bread", range: null })).toBe(false);
    expect(isFaded(bread, { tag: "ceramics", range: null })).toBe(true);
  });

  it("needs both the tag and the months to match", () => {
    expect(isFaded(bread, { tag: "bread", range: spring2024 })).toBe(false);
    expect(isFaded(bread, { tag: "bread", range: { from: "2023-01", to: "2023-12" } })).toBe(true);
  });
});
