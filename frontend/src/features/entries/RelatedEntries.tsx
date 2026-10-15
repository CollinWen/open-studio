/**
 * RelatedEntries: the entries closest in meaning to the one being viewed,
 * as a ruled list of titles with their kind. Found by the backend's related
 * feature.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import type { Entry } from "../../types/entry";

export function RelatedEntries({ entries }: { entries: Entry[] }) {
  if (entries.length === 0) return null;

  return (
    <LabelRow rule="single" label="Related">
      <div className="ledger">
        {entries.map((entry) => (
          <Link key={entry.id} to={`/entry/${entry.id}`} className="ledger-line">
            <span className="ledger-title">{entry.title}</span>
            <span className="quiet">{entry.kind}</span>
          </Link>
        ))}
      </div>
    </LabelRow>
  );
}
