/**
 * FilterSummary: the "Filter" line of the browse panel. One word opens or
 * closes the tags and time lines ("show tags & time" / "hide tags & time").
 * While they're closed, what you picked still shows here (the tag in its
 * filled oval, the span of months in words), each one click from cleared,
 * so a closed panel never hides what is narrowing the view.
 *
 * Used by BrowsePanel.
 */

import { WordChoice } from "../../components/WordChoice";
import { formatMonth, type MonthRange } from "./monthRange";

interface Props {
  open: boolean;
  onToggle: () => void;
  tag: string | null;
  range: MonthRange | null;
  onClearTag: () => void;
  onClearRange: () => void;
}

export function FilterSummary({ open, onToggle, tag, range, onClearTag, onClearRange }: Props) {
  return (
    <div className="word-list is-ovals filter-summary">
      <button type="button" className="quiet" aria-expanded={open} onClick={onToggle}>
        {open ? "hide tags & time" : "show tags & time"}
      </button>
      {!open && tag && <WordChoice label={tag} look="oval" active onPick={onClearTag} />}
      {!open && range && (
        <button type="button" className="clear-word" onClick={onClearRange}>
          {formatMonth(range.from)} – {formatMonth(range.to)} ×
        </button>
      )}
    </div>
  );
}
