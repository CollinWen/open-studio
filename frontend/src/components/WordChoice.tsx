/**
 * WordChoice: a control that is just a word. Soft ink until picked. Put
 * several inside a `.word-list` to space them evenly.
 *
 * How a picked word looks depends on what it is:
 * - "underline" (default) for modes, where one is always on: views, sorts,
 *   visibility, tag importance.
 * - "pill" for filters, which narrow what you see and can be cleared: tags
 *   and years. The pill (ink background) makes it obvious something is on.
 */

interface Props {
  label: string;
  active: boolean;
  onPick: () => void;
  look?: "underline" | "pill";
  /** Overrides the unpicked ink, e.g. key tags in full ink. */
  className?: string;
}

export function WordChoice({ label, active, onPick, look = "underline", className = "quiet" }: Props) {
  const picked = look === "pill" ? "pill" : "is-active";
  return (
    <button type="button" className={active ? picked : className} onClick={onPick}>
      {label}
    </button>
  );
}
