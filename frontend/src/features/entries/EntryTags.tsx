/**
 * EntryTags: an entry's tags, each in the same thin oval as on a board's
 * browse panel. Each one leads back to the entry's own board with that tag
 * highlighted. Used by WallLabel.
 */

import { Link } from "react-router-dom";
import { boardPath } from "../grid/boardPath";

export function EntryTags({ tags, board }: { tags: string[]; board: string }) {
  return (
    <span className="word-list is-ovals">
      {tags.map((tag) => (
        <Link key={tag} className="oval" to={`${boardPath(board)}?tag=${encodeURIComponent(tag)}`}>
          {tag}
        </Link>
      ))}
    </span>
  );
}
