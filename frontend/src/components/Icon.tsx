/**
 * Icon: the site's few marks that aren't words, drawn as thin lines in the
 * ink color so they sit with the rules and type: "caret" (opens and closes
 * a control band's extra lines; turns a quarter when open), "plus" (add),
 * "close" (a thin ×, in the corner of the entry form) and "rows" (three
 * lines: the board's rows view, beside the picture-size dots), and the
 * text editor's marks: "bold" (a B), "italic" (a slanted I), "link" (two
 * chain links), "list" (three lines with square bullets), "quote" (a bar
 * beside lines) and "preview" (an eye).
 * Always inside a button or link that carries the words for screen readers.
 *
 * Looks: .icon in styles/controls.css (line width, size, the caret's turn).
 */

export type IconName = "caret" | "plus" | "close" | "rows" | "bold" | "italic" | "link" | "list" | "quote" | "preview";

// Drawn on a 16 × 16 square, as open strokes.
const STROKES: Record<IconName, string> = {
  caret: "M6 3.5 L10.5 8 L6 12.5",
  plus: "M8 2.5 V13.5 M2.5 8 H13.5",
  close: "M3.5 3.5 L12.5 12.5 M12.5 3.5 L3.5 12.5",
  rows: "M2.5 4 H13.5 M2.5 8 H13.5 M2.5 12 H13.5",
  bold: "M4.5 2.5 V13.5 M4.5 2.5 H8.75 A2.75 2.75 0 0 1 8.75 8 H4.5 M4.5 8 H9.25 A2.75 2.75 0 0 1 9.25 13.5 H4.5",
  italic: "M7 2.5 H12.5 M3.5 13.5 H9 M9.75 2.5 L6.25 13.5",
  link: "M6.5 9.5 L9.5 6.5 M8.25 4.75 L9.5 3.5 A2.47 2.47 0 0 1 12.5 6.5 L11.25 7.75 M7.75 11.25 L6.5 12.5 A2.47 2.47 0 0 1 3.5 9.5 L4.75 8.25",
  list: "M6 4 H13.5 M6 8 H13.5 M6 12 H13.5 M2.5 4 H3 M2.5 8 H3 M2.5 12 H3",
  quote: "M3 2.5 V13.5 M6 4.5 H13 M6 8 H13 M6 11.5 H10.5",
  preview: "M1.5 8 C4 3.5 12 3.5 14.5 8 C12 12.5 4 12.5 1.5 8 Z M8 6 A2 2 0 1 0 8 10 A2 2 0 1 0 8 6 Z",
};

export function Icon({ name }: { name: IconName }) {
  return (
    <svg className={`icon icon-${name}`} viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path d={STROKES[name]} />
    </svg>
  );
}
