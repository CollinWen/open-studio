/**
 * BrowseControls: the first line of the browse panel. A search field, then
 * the views (three dots for small, medium and large pictures, and three
 * lines for rows), then the sort orders, then "clear" when anything is
 * picked or searched. The current view and sort sit on a solid ink square.
 * Sits in the first line of the board's ControlBand (BrowsePanel).
 */

import { Icon } from "../../components/Icon";
import { Dot, MarkChoice } from "../../components/MarkChoice";
import { SearchField } from "../../components/SearchField";
import { WordChoice } from "../../components/WordChoice";
import { DEFAULT_VIEW, SORTS, type Sort, type View } from "./useBrowseParams";

interface Props {
  query: string;
  view: View;
  sort: Sort;
  defaultSort: Sort;
  hasFilters: boolean;
  onChange: (name: "q" | "view" | "sort", value: string | null) => void;
  onClear: () => void;
}

const PICTURE_SIZES = ["small", "medium", "large"] as const;

export function BrowseControls({ query, view, sort, defaultSort, hasFilters, onChange, onClear }: Props) {
  const pickView = (option: View) => onChange("view", option === DEFAULT_VIEW ? null : option);
  const sorts = SORTS.filter((option) => option !== "relevance" || query);

  return (
    <div className="browse-controls">
      <SearchField value={query} onSearch={(words) => onChange("q", words || null)} />
      <span className="mark-list" role="group" aria-label="view">
        {PICTURE_SIZES.map((size) => (
          <MarkChoice
            key={size}
            mark={<Dot size={size} />}
            label={`${size} pictures`}
            active={view === size}
            onPick={() => pickView(size)}
          />
        ))}
        <MarkChoice mark={<Icon name="rows" />} label="rows" active={view === "rows"} onPick={() => pickView("rows")} />
      </span>
      <span className="word-list" role="group" aria-label="sort">
        {sorts.map((option) => (
          <WordChoice
            key={option}
            label={option}
            active={option === sort}
            onPick={() => onChange("sort", option === defaultSort ? null : option)}
          />
        ))}
      </span>
      {hasFilters && (
        <button type="button" className="clear-word" onClick={onClear}>
          clear ×
        </button>
      )}
    </div>
  );
}
