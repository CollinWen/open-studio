/**
 * Tests for sortEntries: pinned entries come first in every order but a
 * search's, keeping the chosen order among themselves.
 */

import { describe, expect, it } from "vitest";
import { sortEntries } from "../../../src/features/grid/sortEntries";
import { makeEntry } from "../../makeEntry";

const entries = [
  makeEntry({ id: "old", title: "b", occurred_at: "2020-01-01" }),
  makeEntry({ id: "pinned-old", title: "c", occurred_at: "2021-01-01", pinned: true }),
  makeEntry({ id: "new", title: "a", occurred_at: "2024-01-01" }),
  makeEntry({ id: "pinned-new", title: "d", occurred_at: "2023-01-01", pinned: true }),
];
const ids = (sorted: typeof entries) => sorted.map((entry) => entry.id);

describe("sortEntries", () => {
  it("puts pinned entries first, newest first among each", () => {
    expect(ids(sortEntries(entries, "recent"))).toEqual(["pinned-new", "pinned-old", "new", "old"]);
  });

  it("keeps pinned first when sorting oldest first or by title", () => {
    expect(ids(sortEntries(entries, "oldest"))).toEqual(["pinned-old", "pinned-new", "old", "new"]);
    expect(ids(sortEntries(entries, "title"))).toEqual(["pinned-old", "pinned-new", "new", "old"]);
  });

  it("keeps a search's order, pinned or not", () => {
    expect(ids(sortEntries(entries, "relevance"))).toEqual(ids(entries));
  });
});
