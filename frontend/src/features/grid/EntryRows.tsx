/**
 * EntryRows: the "rows" view. One line per entry in a Ledger: date, title
 * (with "by <agent>" when an agent added it), kind and tags. No pictures;
 * good for scanning a lot at once. Faded rows don't match the picked tag
 * or months, same as the grid. Given arriveOrder, each row rises in when
 * its page arrives (.is-arriving).
 */

import type { CSSProperties } from "react";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { Entry } from "../../types/entry";
import { isFaded, type Highlight } from "./entryHighlight";

interface Props {
  entries: Entry[];
  highlight: Highlight;
  arriveOrder?: (entry: Entry) => number;
}

const COLUMNS = [
  { label: "date", span: 3 },
  { label: "title", span: 5 },
  { label: "kind", span: 2 },
  { label: "tags", span: 2 },
];

export function EntryRows({ entries, highlight, arriveOrder }: Props) {
  return (
    <Ledger columns={COLUMNS}>
      {entries.map((entry) => (
        <LedgerRow
          key={entry.id}
          to={`/entry/${entry.id}`}
          className={[isFaded(entry, highlight) && "is-faded", arriveOrder && "is-arriving"].filter(Boolean).join(" ")}
          style={arriveOrder && ({ "--arrive-order": arriveOrder(entry) } as CSSProperties)}
          cells={[
            <span className="quiet">{entry.occurred_at.slice(0, 10)}</span>,
            <>
              {entry.title}
              {entry.added_by !== "owner" && <span className="quiet"> by {entry.added_by.replace("agent:", "")}</span>}
            </>,
            <span className="quiet">{entry.kind}</span>,
            <span className="quiet">{entry.tags.join(", ")}</span>,
          ]}
        />
      ))}
    </Ledger>
  );
}
