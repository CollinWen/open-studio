/**
 * WordChoice: a control that is just a word. Soft ink until picked. Put
 * several inside a `.word-list` to space them evenly.
 *
 * How it looks depends on what it is:
 * - "underline" (default) for modes, where one is always on: views, sorts,
 *   visibility, tag importance. The picked one is underlined.
 * - "oval" for filters you can turn on and off (tags): each sits in a thin
 *   flat oval, so it reads as something you can pick; picked, the oval
 *   fills with ink.
 */

interface Props {
  label: string;
  active: boolean;
  onPick: () => void;
  look?: "underline" | "oval";
  /** Overrides the unpicked ink, e.g. key tags in full ink. */
  className?: string;
}

export function WordChoice({ label, active, onPick, look = "underline", className = "quiet" }: Props) {
  const classes =
    look === "oval" ? ["oval", active ? "is-picked" : className] : [active ? "is-active" : className];
  return (
    <button type="button" className={classes.join(" ")} aria-pressed={active} onClick={onPick}>
      {label}
    </button>
  );
}
