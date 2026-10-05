/**
 * EntryTags: an entry's tags as words. Each one leads back to the map with
 * that tag highlighted.
 */

import { Link } from "react-router-dom";

export function EntryTags({ tags }: { tags: string[] }) {
  if (tags.length === 0) return null;

  return (
    <p className="quiet">
      {tags.map((tag, index) => (
        <span key={tag}>
          {index > 0 && ", "}
          <Link to={`/?tag=${encodeURIComponent(tag)}`}>{tag}</Link>
        </span>
      ))}
    </p>
  );
}
