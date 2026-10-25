/**
 * LoadingWord: a word that breathes slowly while something is on its way
 * ("loading", "searching", "saving…"). The one sign of waiting on the site:
 * pages put it on the far right of the header, forms beside their buttons.
 *
 * Looks: .loading-word in global.css.
 */

import type { ReactNode } from "react";

export function LoadingWord({ children = "loading" }: { children?: ReactNode }) {
  return <span className="loading-word">{children}</span>;
}
