/**
 * EntryRows: the "rows" view. One plain line per entry: date, title, kind
 * and tags. No pictures; good for scanning a lot at once.
 * Faded rows don't match the selected tag, same as the grid.
 */

import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";

interface Props {
  entries: Entry[];
  activeTag: string | null;
}

export function EntryRows({ entries, activeTag }: Props) {
  return (
    <div className="entry-rows">
      {entries.map((entry) => (
        <Link
          key={entry.id}
          to={`/entry/${entry.id}`}
          className={activeTag && !entry.tags.includes(activeTag) ? "entry-row is-faded" : "entry-row"}
        >
          <span className="quiet">{entry.occurred_at.slice(0, 10)}</span>
          <span className="entry-row-title">{entry.title}</span>
          <span className="quiet">{entry.kind}</span>
          <span className="quiet">{entry.tags.join(", ")}</span>
        </Link>
      ))}
    </div>
  );
}
