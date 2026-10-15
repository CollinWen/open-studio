/**
 * LabelRow: one row of the 12-column page grid. A quiet label hangs in
 * columns 1–3 ("Tags", "Date"); whatever is passed as children fills columns
 * 4–12. A `wide` row puts its children across all twelve columns, under the
 * label (for the sphere and picture grid).
 *
 * `rule` starts a new section with a line above the row: "double" for major
 * breaks (under the header, before the work, before the footer), "single"
 * for minor ones. The grid, spacing and rules live in global.css (.label-row).
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
      <div className="label-row-label">{label}</div>
      <div className="label-row-content">{children}</div>
    </div>
  );
}
