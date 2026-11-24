/**
 * useBoardPlace: going Back to a board puts the visitor where they were,
 * instead of at the top. While a board is scrolled, it notes which card is
 * at the top of the screen, how far down it sits and how many cards are
 * drawn, for this step of the browser's history (sessionStorage). Coming
 * back to that step (Back or Forward), the board draws that many cards
 * again and scrolls the noted card to the same place once it's there,
 * re-aligning while pictures above it load, until the visitor scrolls.
 *
 * Needed because a board reloads its entries and draws only a few screens
 * of them at first (useShownCount), so the browser alone has nothing to
 * scroll back to. Used by BoardPage. New pages start at the top
 * (components/ScrollToTopOnNewPage.tsx).
 */

import { useEffect, useMemo, useRef } from "react";
import { useLocation, useNavigationType } from "react-router-dom";

export interface BoardPlace {
  // The card at the top of the screen (its link), and how far below the top of the screen it was.
  card: string;
  top: number;
  // How many cards were drawn.
  count: number;
}

const STORAGE_PREFIX = "open-studio-board-place:";
const NOTE_EVERY_MS = 150;
// How long to keep re-aligning while pictures above the card load.
const SETTLE_MS = 2000;
const CARDS = 'main a[href^="/entry/"]';

/** Where the visitor was on this step of history, if they came back to it (Back from another board too). */
export function useSavedBoardPlace(): BoardPlace | null {
  const { key } = useLocation();
  const navigationType = useNavigationType();
  return useMemo(() => (navigationType === "POP" ? readPlace(key) : null), [key, navigationType]);
}

/** Notes the place while scrolling, and goes back to `saved` once its card is drawn. */
export function useBoardPlace(saved: BoardPlace | null, shownCount: number, drawnCount: number) {
  const { key } = useLocation();
  const counted = useRef(shownCount);
  counted.current = shownCount;
  // The place already gone back to, so it happens once per return.
  const restored = useRef<BoardPlace | null>(null);

  useEffect(() => {
    let waiting: number | undefined;
    const note = () => {
      if (waiting !== undefined) return;
      waiting = window.setTimeout(() => {
        waiting = undefined;
        writePlace(key, placeOnScreen(counted.current));
      }, NOTE_EVERY_MS);
    };
    window.addEventListener("scroll", note, { passive: true });
    return () => {
      window.removeEventListener("scroll", note);
      window.clearTimeout(waiting);
    };
  }, [key]);

  useEffect(() => {
    if (!saved || restored.current === saved) return;
    const card = document.querySelector<HTMLElement>(`${CARDS}[href="${CSS.escape(saved.card)}"]`);
    if (!card) return; // not drawn yet: tried again when more are
    const align = () => {
      const offset = card.getBoundingClientRect().top - saved.top;
      if (Math.abs(offset) > 1) window.scrollBy(0, offset);
    };
    align();
    // Pictures above the card load and push it down; keep it in place until they're in or the visitor scrolls.
    const watcher = new ResizeObserver(align);
    watcher.observe(document.body);
    const stop = () => {
      watcher.disconnect();
      restored.current = saved;
    };
    const timer = window.setTimeout(stop, SETTLE_MS);
    const byVisitor = ["wheel", "touchstart", "keydown", "mousedown"];
    byVisitor.forEach((name) => window.addEventListener(name, stop, { once: true, passive: true }));
    return () => {
      watcher.disconnect();
      window.clearTimeout(timer);
      byVisitor.forEach((name) => window.removeEventListener(name, stop));
    };
  }, [saved, drawnCount]);
}

function placeOnScreen(count: number): BoardPlace | null {
  let best: BoardPlace | null = null;
  for (const card of document.querySelectorAll<HTMLElement>(CARDS)) {
    const top = card.getBoundingClientRect().top;
    // The highest card whose top is on screen.
    if (top >= 0 && top < window.innerHeight && (!best || top < best.top)) {
      best = { card: card.getAttribute("href") ?? "", top, count };
    }
  }
  return best;
}

function readPlace(key: string): BoardPlace | null {
  try {
    const text = sessionStorage.getItem(STORAGE_PREFIX + key);
    return text ? (JSON.parse(text) as BoardPlace) : null;
  } catch {
    return null;
  }
}

function writePlace(key: string, place: BoardPlace | null) {
  try {
    if (place) sessionStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(place));
    else sessionStorage.removeItem(STORAGE_PREFIX + key);
  } catch {
    // Storage blocked (private window): Back just starts at the top, as before.
  }
}
