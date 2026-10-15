/**
 * entryHighlight: the one rule every home-page view uses to decide which
 * entries stand out. Picking a tag or some years highlights the entries
 * that match (the tag, and any one of the years); the rest fade (not hide), so crossovers stay visible.
 *
 * Used by SphereView, EntryGrid and EntryRows. The picks themselves live in
 * the URL (useBrowseParams).
 */

import type { Entry } from "../../types/entry";

export interface Highlight {
  tag: string | null;
  /** Empty when no year is picked. */
  years: string[];
}

/** The year an entry belongs to, as written in the URL and the Years row ("2024"). */
export function yearOf(entry: Entry): string {
  return entry.occurred_at.slice(0, 4);
}

/** True when the entry should fade: something is picked and this entry doesn't match it. */
export function isFaded(entry: Entry, highlight: Highlight): boolean {
  if (highlight.tag !== null && !entry.tags.includes(highlight.tag)) return true;
  if (highlight.years.length > 0 && !highlight.years.includes(yearOf(entry))) return true;
  return false;
}
