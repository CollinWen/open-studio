/**
 * BrowseControls: the last line of the browse panel. A search field, then
 * the views (sphere, three dots for small, medium and large pictures, rows),
 * then the sort orders, then "clear" when anything is picked or searched.
 * The current view and sort are underlined (the dots fill in). The sphere
 * arranges entries by time on its own, so sorting is hidden there.
 */

import { useEffect, useState } from "react";
import { DotChoice } from "../../components/DotChoice";
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

const SEARCH_DELAY_MS = 300;
const PICTURE_SIZES = ["small", "medium", "large"] as const;

export function BrowseControls({ query, view, sort, defaultSort, hasFilters, onChange, onClear }: Props) {
  const [typed, setTyped] = useState(query);

  // Follow the URL when it changes from outside (back button, a shared link, "clear").
  useEffect(() => {
    setTyped((current) => (current.trim() === query ? current : query));
  }, [query]);

  // Wait for a pause in typing before searching, so each keystroke isn't a request.
  useEffect(() => {
    if (typed.trim() === query) return;
    const timer = setTimeout(() => onChange("q", typed.trim() || null), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [typed, query, onChange]);

  const pickView = (option: View) => onChange("view", option === DEFAULT_VIEW ? null : option);
  const sorts = SORTS.filter((option) => option !== "relevance" || query);

  return (
    <div className="browse-controls">
      <input
        className="search-field"
        type="search"
        placeholder="search"
        value={typed}
        onChange={(event) => setTyped(event.target.value)}
      />
      <span className="word-list view-choice">
        <WordChoice label="sphere" active={view === "sphere"} onPick={() => pickView("sphere")} />
        <span className="dot-list">
          {PICTURE_SIZES.map((size) => (
            <DotChoice
              key={size}
              size={size}
              label={`${size} pictures`}
              active={view === size}
              onPick={() => pickView(size)}
            />
          ))}
        </span>
        <WordChoice label="rows" active={view === "rows"} onPick={() => pickView("rows")} />
      </span>
      {view !== "sphere" && (
        <span className="word-list">
          {sorts.map((option) => (
            <WordChoice
              key={option}
              label={option}
              active={option === sort}
              onPick={() => onChange("sort", option === defaultSort ? null : option)}
            />
          ))}
        </span>
      )}
      {hasFilters && (
        <button type="button" className="clear-word" onClick={onClear}>
          clear ×
        </button>
      )}
    </div>
  );
}
