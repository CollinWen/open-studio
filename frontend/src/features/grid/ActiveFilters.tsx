/**
 * ActiveFilters: what is narrowing the home page right now (a tag, any
 * picked years, a search), as pills beside the browse controls. Each pill's
 * × clears just that one; "clear all" appears when there are several.
 * Shows nothing when no filter is on.
 *
 * Used by HomePage. The filters themselves live in the URL (useBrowseParams).
 */

import type { Param } from "./useBrowseParams";

interface Props {
  tag: string | null;
  pickedYears: string[];
  query: string;
  onToggleYear: (year: string) => void;
  onClear: (names: Param[]) => void;
}

export function ActiveFilters({ tag, pickedYears, query, onToggleYear, onClear }: Props) {
  const pills = [
    ...(tag ? [{ key: "tag", label: tag, clear: () => onClear(["tag"]) }] : []),
    ...pickedYears.map((year) => ({ key: year, label: year, clear: () => onToggleYear(year) })),
    ...(query ? [{ key: "q", label: `“${query}”`, clear: () => onClear(["q"]) }] : []),
  ];
  if (pills.length === 0) return null;

  return (
    <span className="word-list">
      {pills.map((pill) => (
        <button key={pill.key} type="button" className="pill" onClick={pill.clear}>
          {pill.label} ×
        </button>
      ))}
      {pills.length > 1 && (
        <button type="button" onClick={() => onClear(["tag", "year", "q"])}>
          clear all
        </button>
      )}
    </span>
  );
}
