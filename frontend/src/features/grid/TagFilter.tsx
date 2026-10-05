/**
 * TagFilter: the tags in use, as a plain line of words above the grid.
 * Key tags come first and in black. Clicking one highlights the entries that
 * have it (the rest fade) and shows its description; clicking again clears it.
 */

import type { Tag } from "../../types/entry";

interface Props {
  tags: Tag[];
  activeTag: string | null;
  onSelect: (tag: string | null) => void;
}

export function TagFilter({ tags, activeTag, onSelect }: Props) {
  if (tags.length === 0) return null;

  return (
    <nav className="tag-filter">
      {tags.map((tag) => {
        const classes = [tag.importance === 1 && "is-key", tag.name === activeTag && "is-active"].filter(Boolean);
        return (
          <button
            key={tag.name}
            type="button"
            className={classes.join(" ") || undefined}
            onClick={() => onSelect(tag.name === activeTag ? null : tag.name)}
          >
            {tag.name}
          </button>
        );
      })}
    </nav>
  );
}
