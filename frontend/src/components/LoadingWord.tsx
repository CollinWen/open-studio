/**
 * LoadingWord: the sign that something small is on its way ("loading",
 * "searching", "saving…"): the studio mark sweeping beside a soft word.
 * Pages put it on the far right of the header, forms beside their buttons.
 * Screen readers hear the word, politely, once.
 *
 * Not here: the larger mark that stands in for a whole view still on its
 * way (LoadingMark.tsx). Looks: .loading-word in global.css.
 */

import type { ReactNode } from "react";
import { StudioMark } from "./StudioMark";

export function LoadingWord({ children = "loading" }: { children?: ReactNode }) {
  return (
    <span className="loading-word" role="status">
      <StudioMark playing />
      {children}
    </span>
  );
}
