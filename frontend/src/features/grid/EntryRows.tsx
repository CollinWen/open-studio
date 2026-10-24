/**
 * EntryRows: the "rows" view. One plain line per entry: date, title (with
 * "by <agent>" when an agent added it), kind and tags. No pictures; good for scanning a lot at once.
 * Faded rows don't match the picked tag or year, same as the grid.
 * Given arriveOrder, each row rises in when its page arrives (.is-arriving).
 */

import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";
import { isFaded, type Highlight } from "./entryHighlight";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  arriveOrder?: (entry: Entry) => number;
}

export function EntryRows({ entries, highlight, arriveOrder }: Props) {
  return (
    <div className="entry-rows">
      {entries.map((entry) => (
        <Link
          key={entry.id}
          to={`/entry/${entry.id}`}
          className={["entry-row", isFaded(entry, highlight) && "is-faded", arriveOrder && "is-arriving"]
            .filter(Boolean)
            .join(" ")}
          style={arriveOrder && ({ "--arrive-order": arriveOrder(entry) } as CSSProperties)}
        >
          <span className="quiet">{entry.occurred_at.slice(0, 10)}</span>
          <span>
            <span className="entry-row-title">{entry.title}</span>
            {entry.added_by !== "owner" && <span className="quiet"> by {entry.added_by.replace("agent:", "")}</span>}
          </span>
          <span className="quiet">{entry.kind}</span>
          <span className="quiet">{entry.tags.join(", ")}</span>
        </Link>
      ))}
    </div>
  );
}
