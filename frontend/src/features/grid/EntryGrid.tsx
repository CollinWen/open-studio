/**
 * EntryGrid: the picture views. Entries flow into columns with images keeping
 * their own shapes (a masonry layout). The size (small, medium, large) sets
 * how many columns there are; see .entry-grid in styles/board.css. The board's
 * brief, when given, is the first card.
 * A card with a place in arriveOrder rises in when its page arrives; one
 * without (a board's first page) comes in with the whole view.
 */

import type { ReactNode } from "react";
import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";
import { isFaded, type Highlight } from "./entryHighlight";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  size: "small" | "medium" | "large";
  arriveOrder?: (entry: Entry) => number | undefined;
  /** The board's brief, set as the first card. */
  lead?: ReactNode;
}

export function EntryGrid({ entries, highlight, size, arriveOrder, lead }: Props) {
  return (
    <div className={`entry-grid entry-grid-${size}`}>
      {lead}
      {entries.map((entry) => (
        <EntryCard
          key={entry.id}
          entry={entry}
          faded={isFaded(entry, highlight)}
          arriveOrder={arriveOrder?.(entry)}
        />
      ))}
    </div>
  );
}
