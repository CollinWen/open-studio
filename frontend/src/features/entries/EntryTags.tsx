/**
 * EntryTags: an entry's tags, each in the same thin oval as on a board's
 * browse panel. Each one leads back to the entry's own board with that tag
 * highlighted.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { boardPath } from "../grid/boardPath";

export function EntryTags({ tags, board }: { tags: string[]; board: string }) {
  if (tags.length === 0) return null;

  return (
    <LabelRow rule="single" label="Tags">
      <span className="word-list is-ovals">
        {tags.map((tag) => (
          <Link key={tag} className="oval" to={`${boardPath(board)}?tag=${encodeURIComponent(tag)}`}>
            {tag}
          </Link>
        ))}
      </span>
    </LabelRow>
  );
}
