/**
 * EntryTags: an entry's tags, in the same aligned columns as a board's tag
 * list. Each one leads back to the entry's own board with that tag
 * highlighted. Part of the entry's words, so no rule above it.
 */

import { Link } from "react-router-dom";
import { PageRow } from "../../components/PageRow";
import { boardPath } from "../grid/boardPath";

export function EntryTags({ tags, board }: { tags: string[]; board: string }) {
  if (tags.length === 0) return null;

  return (
    <PageRow className="is-spaced">
      <span className="word-columns">
        {tags.map((tag) => (
          <Link key={tag} className="quiet" to={`${boardPath(board)}?tag=${encodeURIComponent(tag)}`}>
            {tag}
          </Link>
        ))}
      </span>
    </PageRow>
  );
}
