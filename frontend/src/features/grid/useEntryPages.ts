/**
 * useEntryPages: loads a board's entries a page at a time, one page after
 * another, so the first pictures show right away and the rest fill in
 * behind them instead of the page waiting for everything at once.
 *
 * Returns the entries so far and whether more are still coming. A reload
 * (after a save) fetches quietly and swaps the list in once, so what's on
 * screen doesn't drain and refill. Each entry
 * also gets its place within its own page (arriveOrder), so the views can
 * let a new page rise in one after another without the whole collection
 * waiting on one long stagger. Used by HomePage.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchEntryPage } from "../../api/entriesApi";
import type { Entry } from "../../types/entry";

const PAGE_SIZE = 60;
// The first entries of a page rise one after another; the rest come with the last of them,
// so a page's whole arrival stays under half a second (--stagger in global.css).
const MAX_STAGGER_STEPS = 15;

export function useEntryPages(board: string, enabled: boolean) {
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [loading, setLoading] = useState(false);
  const arriveOrder = useRef(new Map<string, number>());
  const [run, setRun] = useState(0);
  const hasShown = useRef(false);

  useEffect(() => {
    if (!enabled) return;
    let stopped = false;
    const quiet = hasShown.current;
    setLoading(true);

    async function loadEveryPage() {
      let cursor: string | null = null;
      let loaded: Entry[] = [];
      do {
        const page = await fetchEntryPage(board, PAGE_SIZE, cursor);
        if (stopped) return;
        page.entries.forEach((entry, i) => arriveOrder.current.set(entry.id, Math.min(i, MAX_STAGGER_STEPS)));
        loaded = [...loaded, ...page.entries];
        if (!quiet) setEntries(loaded);
        cursor = page.next_cursor;
      } while (cursor);
      setEntries(loaded);
      hasShown.current = true;
    }

    loadEveryPage()
      .catch(() => !stopped && setEntries((current) => current ?? []))
      .finally(() => !stopped && setLoading(false));
    return () => {
      stopped = true;
    };
  }, [board, enabled, run]);

  const reload = useCallback(() => setRun((count) => count + 1), []);
  const orderOf = useCallback((entry: Entry) => arriveOrder.current.get(entry.id) ?? 0, []);
  return { entries, loading, reload, orderOf };
}
