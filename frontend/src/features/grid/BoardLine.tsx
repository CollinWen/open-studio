/**
 * BoardLine: the studio's spaces (boards), as a line of larger words, set
 * apart from the tags below so a space never reads as a filter. Shown even
 * when there is only one board, so you always see which space you're in.
 * The one you're in is underlined in the accent color; each word is a link to that board's own page,
 * so spaces never mix: a board shows only its own entries, tags and time.
 * Switching keeps how you're looking (the view) and drops what you'd picked
 * on the board you left.
 *
 * Used by BrowsePanel. Board addresses come from boardPath.ts.
 */

import { Link } from "react-router-dom";
import type { Board } from "../../types/entry";
import { boardPath } from "./boardPath";
import type { View } from "./useBrowseParams";
import { DEFAULT_VIEW } from "./useBrowseParams";

interface Props {
  boards: Board[];
  current: string;
  view: View;
}

export function BoardLine({ boards, current, view }: Props) {
  if (boards.length === 0) return null;
  const search = view === DEFAULT_VIEW ? "" : `?view=${view}`;

  return (
    <nav className="word-list board-line" aria-label="Spaces">
      {boards.map((board) => (
        <Link
          key={board.slug}
          to={`${boardPath(board.slug)}${search}`}
          className={board.slug === current ? "is-active" : "quiet"}
          aria-current={board.slug === current ? "page" : undefined}
        >
          {board.name.toLowerCase()}
        </Link>
      ))}
    </nav>
  );
}
