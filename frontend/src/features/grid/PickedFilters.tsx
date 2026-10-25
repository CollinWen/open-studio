/**
 * PickedFilters: what is narrowing a board while its tags and time are
 * closed: the picked tag in its filled oval, the span of months in an oval
 * too. Clicking one clears it. Shown beside the control band's caret.
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
    <span className="word-list is-ovals">
      {tag && <WordChoice label={tag} look="oval" active onPick={onClearTag} />}
      {range && (
        <WordChoice
          label={`${formatMonth(range.from)} – ${formatMonth(range.to)}`}
          look="oval"
          active
          onPick={onClearRange}
        />
      )}
    </span>
  );
}
