/**
 * EntryGrid: the picture views. Entries are dealt into columns in turn
 * (first to the first column, second to the second, and so on), each column
 * a stack of cards with pictures keeping their own shapes (a masonry layout).
 * Dealing in turn, rather than letting the browser balance the columns,
 * means more entries only ever add to the bottom: what's on screen stays
 * put as the board draws further (useShownCount). The size (small, medium,
 * large) and the screen set how many columns (--grid-columns, read by
 * useGridColumns; see .entry-grid in global.css).
 * Given arriveOrder, each card rises in when its page arrives.
 */

import { useRef } from "react";
import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";
import { isFaded, type Highlight } from "./entryHighlight";
import { useGridColumns } from "./useGridColumns";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  size: "small" | "medium" | "large";
  arriveOrder?: (entry: Entry) => number;
}

export function EntryGrid({ entries, highlight, size, arriveOrder }: Props) {
  const grid = useRef<HTMLDivElement>(null);
  const columnCount = useGridColumns(grid, size);
  const columns: Entry[][] = Array.from({ length: columnCount }, () => []);
  entries.forEach((entry, index) => columns[index % columnCount].push(entry));

  return (
    <div ref={grid} className={`entry-grid entry-grid-${size}`}>
      {columns.map((column, index) => (
        <div key={index} className="entry-grid-column">
          {column.map((entry) => (
            <EntryCard
              key={entry.id}
              entry={entry}
              faded={isFaded(entry, highlight)}
              arriveOrder={arriveOrder?.(entry)}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
