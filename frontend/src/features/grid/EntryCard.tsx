/**
 * EntryCard: one entry in the home grid. Its cover picture (if any), then a
 * small wall label: title, "kind · date" (plus how many pictures, if several),
 * and the first lines of "why it's here". A write-up's cover already is its
 * title, so its label skips the title and says "write-up" instead.
 * The whole card links to the entry's page.
 *
 * Faded (not hidden) when a tag filter is on and this entry doesn't match,
 * so crossovers between topics stay visible. With an arriveOrder it rises
 * into place when its page of entries arrives, after the ones before it.
 */

import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";
import { formatDate } from "../entries/formatDate";
import { EntryCover } from "./EntryCover";

interface Props {
  entry: Entry;
  faded: boolean;
  arriveOrder?: number;
}

export function EntryCard({ entry, faded, arriveOrder }: Props) {
  const arriving = arriveOrder !== undefined;
  const isWriteup = entry.media[0]?.type === "html";
  return (
    <Link
      to={`/entry/${entry.id}`}
      className={["entry-card", faded && "is-faded", arriving && "is-arriving"].filter(Boolean).join(" ")}
      style={arriving ? ({ "--arrive-order": arriveOrder } as CSSProperties) : undefined}
    >
      <EntryCover media={entry.media} title={entry.title} />
      {!isWriteup && <span className="entry-card-title">{entry.title}</span>}
      <span className="quiet">
        {entry.kind} · {formatDate(entry.occurred_at)}
        {isWriteup && " · write-up"}
        {entry.media.length > 1 && ` · ${entry.media.length} pictures`}
      </span>
      {entry.description && <span className="entry-card-why">{entry.description}</span>}
    </Link>
  );
}
