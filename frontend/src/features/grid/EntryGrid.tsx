/**
 * EntryGrid: the picture views. Entries flow into columns with images keeping
 * their own shapes (a masonry layout). The size (small, medium, large) sets
 * how wide each column is; see .entry-grid in global.css.
 */

import type { Entry } from "../../types/entry";
import { EntryCard } from "./EntryCard";

interface Props {
  entries: Entry[];
  activeTag: string | null;
  size: "small" | "medium" | "large";
}

export function EntryGrid({ entries, activeTag, size }: Props) {
  return (
    <div className={`entry-grid entry-grid-${size}`}>
      {entries.map((entry) => (
        <EntryCard
          key={entry.id}
          entry={entry}
          faded={activeTag !== null && !entry.tags.includes(activeTag)}
        />
      ))}
    </div>
  );
}
