/**
 * EntryGrid: the picture views. Entries flow into columns with images keeping
 * their own shapes (a masonry layout). The size (small, medium, large) sets
 * how many columns there are; see .entry-grid in global.css.
 * Given arriveOrder, each card rises in when its page arrives.
 */

import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";
import { isFaded, type Highlight } from "./entryHighlight";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  size: "small" | "medium" | "large";
  arriveOrder?: (entry: Entry) => number;
}

export function EntryGrid({ entries, highlight, size, arriveOrder }: Props) {
  return (
    <div className={`entry-grid entry-grid-${size}`}>
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
