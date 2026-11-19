/**
 * useShownCount: how many of a board's entries to draw. A few screens' worth
 * at first, then more each time the visitor scrolls near the end of what's
 * drawn, so a long board never puts hundreds of cards and pictures on the
 * page at once (on a phone that's what keeps it busy and warm). The entries
 * themselves all arrive anyway (useEntryPages): they're small, and the
 * counts, tags and time slider need every one.
 *
 * The returned markerRef goes on an empty element after the list; when it
 * comes within reach, more are drawn. Starts over when startOverKey changes
 * (another board, search or sort). Used by BoardPage.
 */

import { useEffect, useState } from "react";

// Steps that divide evenly into every column count the grid uses (6, 4, 3, 2, 1).
const FIRST_COUNT = 48;
const STEP = 48;
// Draw the next ones this far before the end comes into view, so scrolling never meets a gap.
const AHEAD = "0px 0px 1500px 0px";

export function useShownCount(total: number, startOverKey: string) {
  const [count, setCount] = useState(FIRST_COUNT);
  const [marker, setMarker] = useState<HTMLElement | null>(null);

  useEffect(() => setCount(FIRST_COUNT), [startOverKey]);

  // A new watcher after each step, so a marker still in reach (a short page) asks again at once.
  useEffect(() => {
    if (!marker || count >= total) return;
    const watcher = new IntersectionObserver(
      ([seen]) => seen.isIntersecting && setCount((current) => current + STEP),
      { rootMargin: AHEAD },
    );
    watcher.observe(marker);
    return () => watcher.disconnect();
  }, [marker, count, total]);

  return { shownCount: Math.min(count, total), markerRef: setMarker };
}
