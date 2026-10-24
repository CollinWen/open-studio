/**
 * Icon: the site's few marks that aren't words, drawn as thin lines in the
 * ink color so they sit with the rules and type: "caret" (opens and closes
 * a control band's extra lines; turns a quarter when open) and "plus" (add).
 * Always inside a button or link that carries the words for screen readers.
 *
 * Looks: .icon in global.css (line width, size, the caret's turn).
 */

export type IconName = "caret" | "plus";

// Drawn on a 16 × 16 square, as open strokes.
const STROKES: Record<IconName, string> = {
  caret: "M6 3.5 L10.5 8 L6 12.5",
  plus: "M8 2.5 V13.5 M2.5 8 H13.5",
};

export function Icon({ name }: { name: IconName }) {
  return (
    <svg className={`icon icon-${name}`} viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path d={STROKES[name]} />
    </svg>
  );
}
