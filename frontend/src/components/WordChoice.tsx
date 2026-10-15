/**
 * WordChoice: a control that is just a word. Soft ink until picked, then
 * full ink and underlined. Put several inside a `.word-list` to space them
 * evenly ("sphere small medium large rows").
 *
 * Used for every pick-one control: views, sorts, years, visibility, tag
 * importance.
 */

interface Props {
  label: string;
  active: boolean;
  onPick: () => void;
}

export function WordChoice({ label, active, onPick }: Props) {
  return (
    <button type="button" className={active ? "is-active" : "quiet"} onClick={onPick}>
      {label}
    </button>
  );
}
