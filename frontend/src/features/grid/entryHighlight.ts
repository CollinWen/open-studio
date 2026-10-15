/**
 * entryHighlight: the one rule every home-page view uses to decide which
 * entries stand out. Picking a tag or a year highlights the entries that
 * match; the rest fade (not hide), so crossovers stay visible.
 *
 * Used by SphereView, EntryGrid and EntryRows. The picks themselves live in
 * the URL (useBrowseParams).
 */

import type { Entry } from "../../types/entry";

export interface Highlight {
  tag: string | null;
  year: string | null;
}

/** The year an entry belongs to, as written in the URL and the Year row ("2024"). */
export function yearOf(entry: Entry): string {
  return entry.occurred_at.slice(0, 4);
}

/** True when the entry should fade: something is picked and this entry doesn't match it. */
export function isFaded(entry: Entry, highlight: Highlight): boolean {
  if (highlight.tag !== null && !entry.tags.includes(highlight.tag)) return true;
  if (highlight.year !== null && yearOf(entry) !== highlight.year) return true;
  return false;
}
