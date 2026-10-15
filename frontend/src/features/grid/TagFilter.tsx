/**
 * TagFilter: the tags in use, as two lines of words. Key tags (set in the
 * studio) get the first line, in full ink; every other tag follows on the
 * next line in soft ink. Clicking one picks it: it turns into a pill,
 * entries without it fade, and its description becomes the intro. Clicking
 * it again clears it.
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

  const lineOf = (group: Tag[], ink: string) =>
    group.length > 0 && (
      <div className="word-list">
        {group.map((tag) => (
          <WordChoice
            key={tag.name}
            label={tag.name}
            look="pill"
            className={ink}
            active={tag.name === activeTag}
            onPick={() => onSelect(tag.name === activeTag ? null : tag.name)}
          />
        ))}
      </div>
    );

  return (
    <nav className="tag-filter">
      {lineOf(keyTags, "")}
      {lineOf(otherTags, "quiet")}
    </nav>
  );
}
