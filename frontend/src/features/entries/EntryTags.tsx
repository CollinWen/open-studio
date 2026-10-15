/**
 * EntryTags: an entry's tags as a row of words. Each one leads back to the
 * home page with that tag highlighted.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";

export function EntryTags({ tags }: { tags: string[] }) {
  if (tags.length === 0) return null;

  return (
    <LabelRow rule="single" label="Tags">
      <span className="word-list">
        {tags.map((tag) => (
          <Link key={tag} to={`/?tag=${encodeURIComponent(tag)}`}>
            {tag}
          </Link>
        ))}
      </span>
    </LabelRow>
  );
}
