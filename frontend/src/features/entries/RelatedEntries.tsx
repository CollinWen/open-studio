/**
 * RelatedEntries: the entries closest in meaning to the one being viewed,
 * as a list of titles with their kind under the quiet word "related". It
 * flows on from the entry with space, not a rule. Found by the backend's
 * related feature.
 */

import { Link } from "react-router-dom";
import { PageRow } from "../../components/PageRow";
import type { Entry } from "../../types/entry";

export function RelatedEntries({ entries }: { entries: Entry[] }) {
  if (entries.length === 0) return null;

  return (
    <PageRow className="is-spaced">
      <div className="related-list">
        <p className="quiet related-heading">related</p>
        {entries.map((entry) => (
          <Link key={entry.id} to={`/entry/${entry.id}`} className="related-line">
            <span className="related-title">{entry.title}</span>
            <span className="quiet">{entry.kind}</span>
          </Link>
        ))}
      </div>
    </PageRow>
  );
}
