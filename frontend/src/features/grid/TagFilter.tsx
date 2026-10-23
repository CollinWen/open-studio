/**
 * TagFilter: the board's tags, each in a thin flat oval so it reads as
 * something to pick. Key tags (set in the studio) come first, in full ink;
 * every other tag follows in soft ink. Clicking one picks it: its oval fills
 * with ink, entries without it fade, and its description becomes the intro.
 * Clicking it again clears it.
 */

import { WordChoice } from "../../components/WordChoice";
import type { Tag } from "../../types/entry";

interface Props {
  tags: Tag[];
  activeTag: string | null;
  onSelect: (tag: string | null) => void;
}

export function TagFilter({ tags, activeTag, onSelect }: Props) {
  if (tags.length === 0) return null;
  const keyTags = tags.filter((tag) => tag.importance === 1);
  const otherTags = tags.filter((tag) => tag.importance !== 1);

  return (
    <div className="word-list is-ovals">
      {[...keyTags, ...otherTags].map((tag) => (
        <WordChoice
          key={tag.name}
          label={tag.name}
          look="oval"
          className={tag.importance === 1 ? "is-key" : "quiet"}
          active={tag.name === activeTag}
          onPick={() => onSelect(tag.name === activeTag ? null : tag.name)}
        />
      ))}
    </div>
  );
}
