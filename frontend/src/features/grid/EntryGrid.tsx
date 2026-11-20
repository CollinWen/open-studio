/**
 * EntryGrid: the picture views. Entries are dealt into columns in turn
 * (first to the first column, second to the second, and so on), each column
 * a stack of framed cards with pictures keeping their own shapes (a masonry
 * layout). Dealing in turn, rather than letting the browser balance the
 * columns, means more entries only ever add to the bottom: what's on screen
 * stays put as the board draws further (useShownCount). The size (small,
 * medium, large) and the screen set how many columns (--grid-columns, read
 * by useGridColumns; see .entry-grid in styles/board.css).
 *
 * The board's brief, when given, is dealt first, so it heads the first
 * column. A card with a place in arriveOrder rises in when its page
 * arrives; one without (a board's first page) comes in with the whole view.
 */

import { useRef, type ReactNode } from "react";
import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";
import { isFaded, type Highlight } from "./entryHighlight";
import { useGridColumns } from "./useGridColumns";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  size: "small" | "medium" | "large";
  arriveOrder?: (entry: Entry) => number | undefined;
  /** The board's brief, set as the first card. */
  lead?: ReactNode;
}

export function EntryGrid({ entries, highlight, size, arriveOrder, lead }: Props) {
  const grid = useRef<HTMLDivElement>(null);
  const columnCount = useGridColumns(grid, size);
  const cards: ReactNode[] = entries.map((entry) => (
    <EntryCard key={entry.id} entry={entry} faded={isFaded(entry, highlight)} arriveOrder={arriveOrder?.(entry)} />
  ));
  if (lead) cards.unshift(<div key="brief">{lead}</div>);
  const columns: ReactNode[][] = Array.from({ length: columnCount }, () => []);
  cards.forEach((card, index) => columns[index % columnCount].push(card));

  return (
    <div ref={grid} className={`entry-grid entry-grid-${size}`}>
      {columns.map((column, index) => (
        <div key={index} className="entry-grid-column">
          {column}
        </div>
      ))}
    </div>
  );
}
