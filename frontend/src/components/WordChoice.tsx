/**
 * WordChoice: a control that is just a word. Put several inside a
 * `.word-list` to space them evenly.
 *
 * How it looks depends on what it is:
 * - "square" (default) for modes, where one is always on: views, sorts,
 *   visibility, boards in the entry form. Each word sits on a square of
 *   shaded paper when pointed at; the picked one sits on a solid ink
 *   square, in paper-colored type, so the pick reads at a glance.
 * - "oval" for filters you can turn on and off (tags): each sits in a thin
 *   flat oval, so it reads as something you can pick; picked, the oval
 *   fills with ink.
 */

interface Props {
  label: string;
  active: boolean;
  onPick: () => void;
  look?: "square" | "oval";
  /** Overrides the unpicked ink, e.g. key tags in full ink. */
  className?: string;
}

export function WordChoice({ label, active, onPick, look = "square", className = "quiet" }: Props) {
  const classes =
    look === "oval" ? ["oval", active ? "is-picked" : className] : ["square", active ? "is-picked" : className];
  return (
    <button type="button" className={classes.join(" ")} aria-pressed={active} onClick={onPick}>
      {label}
    </button>
  );
}
