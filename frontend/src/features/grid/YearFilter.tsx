/**
 * YearFilter: the years that have entries, newest first, as a line of words.
 * Any number can be picked: each picked year turns into a pill, its entries
 * are highlighted in every view, and the sphere turns to face the picked
 * bands. Clicking a picked year again takes it out.
 */

import { WordChoice } from "../../components/WordChoice";

interface Props {
  years: string[];
  pickedYears: string[];
  onToggle: (year: string) => void;
}

export function YearFilter({ years, pickedYears, onToggle }: Props) {
  if (years.length < 2) return null;

  return (
    <nav className="word-list">
      {years.map((year) => (
        <WordChoice
          key={year}
          label={year}
          look="pill"
          active={pickedYears.includes(year)}
          onPick={() => onToggle(year)}
        />
      ))}
    </nav>
  );
}
