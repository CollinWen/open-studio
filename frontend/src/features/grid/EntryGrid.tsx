/**
 * EntryGrid: the picture views. Entries flow into columns with images keeping
 * their own shapes (a masonry layout). The size (small, medium, large) sets
 * how many columns there are; see .entry-grid in global.css.
 */

import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";
import { isFaded, type Highlight } from "./entryHighlight";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  size: "small" | "medium" | "large";
}

export function EntryGrid({ entries, highlight, size }: Props) {
  return (
    <div className={`entry-grid entry-grid-${size}`}>
      {entries.map((entry) => (
        <EntryCard key={entry.id} entry={entry} faded={isFaded(entry, highlight)} />
      ))}
    </div>
  );
}
