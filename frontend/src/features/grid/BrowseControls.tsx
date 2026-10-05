/**
 * BrowseControls: one quiet line above the grid. A search field, then the
 * view sizes (small · medium · large · rows), then the sort orders, all as
 * plain words. The current choice is underlined.
 */

import { useEffect, useState } from "react";
import { SORTS, VIEWS, type Sort, type View } from "./useBrowseParams";

interface Props {
  query: string;
  view: View;
  sort: Sort;
  defaultSort: Sort;
  onChange: (name: "q" | "view" | "sort", value: string | null) => void;
}

const SEARCH_DELAY_MS = 300;

export function BrowseControls({ query, view, sort, defaultSort, onChange }: Props) {
  const [typed, setTyped] = useState(query);

  // Follow the URL when it changes from outside (back button, a shared link).
  useEffect(() => {
    setTyped((current) => (current.trim() === query ? current : query));
  }, [query]);

  // Wait for a pause in typing before searching, so each keystroke isn't a request.
  useEffect(() => {
    if (typed.trim() === query) return;
    const timer = setTimeout(() => onChange("q", typed.trim() || null), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [typed, query, onChange]);

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
      <span>
        {VIEWS.map((option) => (
          <Choice key={option} label={option} active={option === view} onPick={() => onChange("view", option === "medium" ? null : option)} />
        ))}
      </span>
      <span>
        {sorts.map((option) => (
          <Choice key={option} label={option} active={option === sort} onPick={() => onChange("sort", option === defaultSort ? null : option)} />
        ))}
      </span>
    </div>
  );
}

function Choice({ label, active, onPick }: { label: string; active: boolean; onPick: () => void }) {
  return (
    <button type="button" className={active ? "is-active" : "quiet"} onClick={onPick}>
      {label}
    </button>
  );
}
