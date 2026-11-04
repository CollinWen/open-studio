/**
 * WordChoice: a control that is just a word. Soft ink until picked;
 * picked, it's underlined, whether it's a mode (views, sorts, visibility)
 * or a filter you turn on and off (a tag, a board). Put several inside a
 * `.word-list` to space them evenly, or a `.word-columns` to line them up
 * as a list.
 */

interface Props {
  label: string;
  active: boolean;
  onPick: () => void;
  /** Overrides the unpicked ink, e.g. key tags in full ink. */
  className?: string;
}

export function WordChoice({ label, active, onPick, className = "quiet" }: Props) {
  return (
    <button type="button" className={active ? "is-active" : className} aria-pressed={active} onClick={onPick}>
      {label}
    </button>
  );
}
