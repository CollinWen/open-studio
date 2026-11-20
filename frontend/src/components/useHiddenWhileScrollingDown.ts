/**
 * useHiddenWhileScrollingDown: whether a bar stuck to the top of the screen
 * (the site header) should step out of the way. It hides once you scroll
 * down past it, and comes back as soon as you scroll up, or move the
 * pointer up into the strip where it sits. Near the top of the page it is
 * always shown.
 *
 * Pass a ref to the bar; its own height is the strip that brings it back.
 * Used by SiteHeader.
 */

import { useEffect, useState, type RefObject } from "react";

// How far the page must move (in pixels) before it counts, so a trackpad's tremble doesn't flicker it.
const SCROLL_SLACK = 4;

export function useHiddenWhileScrollingDown(bar: RefObject<HTMLElement | null>): boolean {
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    let last = window.scrollY;
    const height = () => bar.current?.offsetHeight ?? 0;

    const onScroll = () => {
      const now = window.scrollY;
      if (now <= height()) setHidden(false);
      else if (now > last + SCROLL_SLACK) setHidden(true);
      else if (now < last - SCROLL_SLACK) setHidden(false);
      if (Math.abs(now - last) > SCROLL_SLACK) last = now;
    };
    const onPointerMove = (event: PointerEvent) => {
      if (event.clientY <= height()) setHidden(false);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("pointermove", onPointerMove, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("pointermove", onPointerMove);
    };
  }, [bar]);

  return hidden;
}
