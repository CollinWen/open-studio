/**
 * entryHighlight: the one rule every board view uses to decide which
 * entries stand out. Picking a tag or a span of months highlights the
 * entries that match both; the rest fade (not hide), so crossovers stay visible.
 *
 * Used by SphereView, EntryGrid and EntryRows. The picks themselves live in
 * the URL (useBrowseParams).
 */

import type { Entry } from "../../types/entry";
import { isInRange, monthOf, type MonthRange } from "./monthRange";

export interface Highlight {
  tag: string | null;
  /** Null when no span of months is picked. */
  range: MonthRange | null;
}

/** True when the entry should fade: something is picked and this entry doesn't match it. */
export function isFaded(entry: Entry, highlight: Highlight): boolean {
  if (highlight.tag !== null && !entry.tags.includes(highlight.tag)) return true;
  if (highlight.range !== null && !isInRange(monthOf(entry), highlight.range)) return true;
  return false;
}
