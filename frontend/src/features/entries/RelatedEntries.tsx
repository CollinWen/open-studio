/**
 * RelatedEntries: the entries closest in meaning to the one being viewed,
 * as a short list of titles. Found by the backend's related feature.
 */

import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";

export function RelatedEntries({ entries }: { entries: Entry[] }) {
  if (entries.length === 0) return null;

  return (
    <section className="related">
      <p className="quiet">related</p>
      {entries.map((entry) => (
        <p key={entry.id}>
          <Link to={`/entry/${entry.id}`}>{entry.title}</Link> <span className="quiet">{entry.kind}</span>
        </p>
      ))}
    </section>
  );
}
