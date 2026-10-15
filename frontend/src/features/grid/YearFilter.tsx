/**
 * YearFilter: the years that have entries, newest first, as a line of words
 * ("all 2026 2025 2024 …"). Picking one highlights that year's entries in
 * every view, and turns the sphere so that year's band faces you. "all"
 * clears it. The current pick is underlined.
 */

import { WordChoice } from "../../components/WordChoice";

interface Props {
  years: string[];
  activeYear: string | null;
  onSelect: (year: string | null) => void;
}

export function YearFilter({ years, activeYear, onSelect }: Props) {
  if (years.length < 2) return null;

  return (
    <nav className="word-list">
      <WordChoice label="all" active={activeYear === null} onPick={() => onSelect(null)} />
      {years.map((year) => (
        <WordChoice key={year} label={year} active={year === activeYear} onPick={() => onSelect(year)} />
      ))}
    </nav>
  );
}
