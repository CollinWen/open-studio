/**
 * ScrollToTopOnNewPage: opening a new page (a link to an entry, another
 * board, about) starts it at the top, instead of where the last page was
 * scrolled to. Going back or forward is left alone (the browser's own
 * doing), and so is a change to the same page's choices (a tag, a view, a
 * search), which only changes the address's ?query.
 *
 * Draws nothing. Used once, in App.
 */

import { useLayoutEffect } from "react";
import { useLocation, useNavigationType } from "react-router-dom";

export function ScrollToTopOnNewPage() {
  const { pathname } = useLocation();
  const navigationType = useNavigationType();

  useLayoutEffect(() => {
    if (navigationType !== "POP") window.scrollTo(0, 0);
  }, [pathname, navigationType]);

  return null;
}
