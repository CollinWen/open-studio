/**
 * EntryCard: one entry in the home grid. Its cover picture (if any), then a
 * small wall label: title, "kind · date" (plus how many pictures, if several),
 * and the first lines of "why it's here".
 * The whole card links to the entry's page.
 *
 * Faded (not hidden) when a tag filter is on and this entry doesn't match,
 * so crossovers between topics stay visible.
 */

import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";
import { formatDate } from "../entries/formatDate";
import { EntryCover } from "./EntryCover";

export function EntryCard({ entry, faded }: { entry: Entry; faded: boolean }) {
  return (
    <Link to={`/entry/${entry.id}`} className={faded ? "entry-card is-faded" : "entry-card"}>
      <EntryCover media={entry.media} title={entry.title} />
      <span className="entry-card-title">{entry.title}</span>
      <span className="quiet">
        {entry.kind} · {formatDate(entry.occurred_at)}
        {entry.media.length > 1 && ` · ${entry.media.length} pictures`}
      </span>
      {entry.description && <span className="entry-card-why">{entry.description}</span>}
    </Link>
  );
}
