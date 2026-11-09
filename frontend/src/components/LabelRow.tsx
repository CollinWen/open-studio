/**
 * LabelRow: one row of the 12-column page grid. Its content starts on the
 * page's one left edge (column 1) and may run across all twelve columns.
 * A `label`, when there is one ("Tags", "Related"), sits above the content
 * as a small, quiet caption, like a heading on a Swiss poster; there is no
 * column of labels hanging beside the content. Most rows need no label:
 * the content says what it is.
 *
 * `rule` starts a new section with a line above the row: "double" for major
 * breaks (under the header, before the work, before the footer), "single"
 * for minor ones. A `wide` row (the picture grid, a list) gets a line of
 * space above its content. The grid, spacing and rules live in global.css
 * (.label-row).
 */

import type { ReactNode } from "react";

interface Props {
  label?: ReactNode;
  rule?: "single" | "double";
  wide?: boolean;
  className?: string;
  children?: ReactNode;
}

export function LabelRow({ label, rule, wide = false, className, children }: Props) {
  const classes = [
    "label-row",
    rule === "single" && "is-ruled",
    rule === "double" && "is-double",
    wide && "is-wide",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={classes}>
      {label && <div className="label-row-label">{label}</div>}
      <div className="label-row-content">{children}</div>
    </div>
  );
}
