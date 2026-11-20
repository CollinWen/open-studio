/**
 * useEntryPages: loads a board's entries a page at a time, one page after
 * another, so the first pictures show right away and the rest fill in
 * behind them instead of the page waiting for everything at once.
 *
 * Switching to another board keeps the one on screen (marked `switching`,
 * so the page can fade it out) until the new board's first page is in and
 * the fade-out has had its time, then swaps it in; that first page fades in whole (it has no
 * arriveOrder), and each later page rises in one entry after another. A
 * reload (after a save) fetches quietly and swaps the list in once, so
 * what's on screen doesn't drain and refill.
 *
 * Returns the entries so far, which board they belong to, and whether more
 * are still coming. Used by BoardPage.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchEntryPage } from "../../api/entriesApi";
import type { Entry } from "../../types/entry";

const PAGE_SIZE = 60;
// The first entries of a page rise one after another; the rest come with the last of them,
// so a page's whole arrival stays under half a second (--stagger in tokens.css).
const MAX_STAGGER_STEPS = 15;
// How long the board on screen takes to fade out (--motion-quick in tokens.css).
const FADE_OUT_MS = 200;

const wait = (ms: number) => new Promise((done) => setTimeout(done, ms));

export function useEntryPages(board: string) {
  const [entries, setEntries] = useState<Entry[] | null>(null);
  // The board the entries on screen belong to (it lags `board` while switching).
  const [entriesBoard, setEntriesBoard] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const arriveOrder = useRef(new Map<string, number>());
  const [run, setRun] = useState(0);
  // The board already fully loaded, if any: reloading it is quiet, a different one swaps in.
  const shownBoard = useRef<string | null>(null);

  useEffect(() => {
    let stopped = false;
    const quiet = shownBoard.current === board;
    const fadingOut = !quiet && shownBoard.current !== null;
    const started = performance.now();
    setLoading(true);

    async function loadEveryPage() {
      let cursor: string | null = null;
      let loaded: Entry[] = [];
      let first = true;
      do {
        const page = await fetchEntryPage(board, PAGE_SIZE, cursor);
        if (first && fadingOut) await wait(FADE_OUT_MS - (performance.now() - started));
        if (stopped) return;
        if (first && !quiet) arriveOrder.current = new Map();
        // The first page of a new board fades in whole, so only later pages get a place in line.
        if (!first || quiet) {
          page.entries.forEach((entry, i) => arriveOrder.current.set(entry.id, Math.min(i, MAX_STAGGER_STEPS)));
        }
        loaded = [...loaded, ...page.entries];
        if (!quiet) {
          setEntries(loaded);
          setEntriesBoard(board);
        }
        first = false;
        cursor = page.next_cursor;
      } while (cursor);
      setEntries(loaded);
      setEntriesBoard(board);
      shownBoard.current = board;
    }

    loadEveryPage()
      .catch(() => {
        if (stopped) return;
        setEntries((current) => (quiet ? (current ?? []) : []));
        setEntriesBoard(board);
      })
      .finally(() => !stopped && setLoading(false));
    return () => {
      stopped = true;
    };
  }, [board, run]);

  const reload = useCallback(() => setRun((count) => count + 1), []);
  const orderOf = useCallback((entry: Entry) => arriveOrder.current.get(entry.id), []);
  const switching = entries !== null && entriesBoard !== board;
  return { entries, entriesBoard, switching, loading, reload, orderOf };
}
