/**
 * sortEntries: puts a board's entries in the chosen order.
 * "relevance" keeps the order the search returned (best match first).
 * Otherwise pinned entries come first, in the chosen order among themselves.
 */

import type { Entry } from "../../types/entry";
import type { Sort } from "./useBrowseParams";

export function sortEntries(entries: Entry[], sort: Sort): Entry[] {
  const sorted = [...entries];
  if (sort === "recent") sorted.sort((a, b) => b.occurred_at.localeCompare(a.occurred_at));
  if (sort === "oldest") sorted.sort((a, b) => a.occurred_at.localeCompare(b.occurred_at));
  if (sort === "title") sorted.sort((a, b) => a.title.localeCompare(b.title));
  if (sort === "relevance") return sorted;
  // A stable sort, so pinned entries keep the chosen order among themselves.
  return sorted.sort((a, b) => Number(b.pinned) - Number(a.pinned));
}
