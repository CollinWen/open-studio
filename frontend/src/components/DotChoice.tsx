/**
 * DotChoice: a pick-one control drawn as a dot, for choices that are a size
 * (small, medium, large pictures): the dot's size says the choice, so it
 * needs no word. Soft ink until picked, full ink when picked. The label is
 * still there for screen readers and as a hover tip.
 *
 * Dot sizes are tokens in global.css (--dot-small, --dot-medium, --dot-large).
 */

interface Props {
  size: "small" | "medium" | "large";
  label: string;
  active: boolean;
  onPick: () => void;
}

export function DotChoice({ size, label, active, onPick }: Props) {
  return (
    <button
      type="button"
      className={`dot-choice dot-${size}${active ? " is-picked" : ""}`}
      aria-label={label}
      aria-pressed={active}
      title={label}
      onClick={onPick}
    />
  );
}
