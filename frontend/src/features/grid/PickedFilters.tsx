/**
 * PickedFilters: what is narrowing a board while its tags and time are
 * closed: the picked tag and the span of months, underlined. Clicking one
 * clears it. Shown beside the control band's caret.
 *
 * Used by BrowsePanel.
 */

import { WordChoice } from "../../components/WordChoice";
import { formatMonth, type MonthRange } from "./monthRange";

interface Props {
  tag: string | null;
  range: MonthRange | null;
  onClearTag: () => void;
  onClearRange: () => void;
}

export function PickedFilters({ tag, range, onClearTag, onClearRange }: Props) {
  if (!tag && !range) return null;
  return (
    <span className="word-list">
      {tag && <WordChoice label={tag} active onPick={onClearTag} />}
      {range && (
        <WordChoice
          label={`${formatMonth(range.from)} – ${formatMonth(range.to)}`}
          active
          onPick={onClearRange}
        />
      )}
    </span>
  );
}
