/**
 * MarkChoice: a pick-one control drawn as a mark instead of a word, in a
 * small square: a dot whose size says the picture size (small, medium,
 * large), or an icon (the rows view). Full ink on the paper until picked;
 * picked, the square fills with ink and the mark turns paper, the same
 * solid square as a picked WordChoice. The label is there for screen
 * readers and as a hover tip.
 *
 * Used by BrowseControls. Looks: .mark-choice and .dot in global.css (dot
 * sizes are the --dot-* tokens).
 */

import type { ReactNode } from "react";

interface Props {
  mark: ReactNode;
  label: string;
  active: boolean;
  onPick: () => void;
}

export function MarkChoice({ mark, label, active, onPick }: Props) {
  return (
    <button
      type="button"
      className={`mark-choice${active ? " is-picked" : ""}`}
      aria-label={label}
      aria-pressed={active}
      title={label}
      onClick={onPick}
    >
      {mark}
    </button>
  );
}

/** A round dot of one of the three sizes, to put in a MarkChoice. */
export function Dot({ size }: { size: "small" | "medium" | "large" }) {
  return <span className={`dot dot-${size}`} aria-hidden="true" />;
}
