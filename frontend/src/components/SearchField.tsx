/**
 * SearchField: a search box drawn as an underline. It searches once typing
 * pauses, so each keystroke isn't a request, and follows `value` when it
 * changes from outside (the back button, a shared link, "clear").
 *
 * Used by every control band that searches. Looks: .search-field.
 */

import { useEffect, useRef, useState } from "react";

const SEARCH_DELAY_MS = 300;

interface Props {
  value: string;
  onSearch: (words: string) => void;
  placeholder?: string;
}

export function SearchField({ value, onSearch, placeholder = "search" }: Props) {
  const [typed, setTyped] = useState(value);
  // The latest onSearch, so a parent re-rendering doesn't restart the wait.
  const search = useRef(onSearch);
  search.current = onSearch;

  useEffect(() => {
    setTyped((current) => (current.trim() === value ? current : value));
  }, [value]);

  useEffect(() => {
    if (typed.trim() === value) return;
    const timer = setTimeout(() => search.current(typed.trim()), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [typed, value]);

  return (
    <input
      className="search-field"
      type="search"
      placeholder={placeholder}
      value={typed}
      onChange={(event) => setTyped(event.target.value)}
    />
  );
}
