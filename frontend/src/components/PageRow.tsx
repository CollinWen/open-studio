/**
 * PageRow: one row of the page, inside the page margins and edge to edge
 * with the 12-column grid. There are no side labels: what's in a row says
 * what it is.
 *
 * `rule` puts a line above the row, and only where the page switches
 * context: "double" for the site's frame (under the header, before the
 * footer), "single" between the parts of a page (a board's intro and its
 * work, an entry's words and its pictures). Inside a part, space does the
 * separating, never a line. The spacing and rules live in global.css
 * (.page-row).
 */

import type { ReactNode } from "react";

interface Props {
  rule?: "single" | "double";
  className?: string;
  children?: ReactNode;
}

export function PageRow({ rule, className, children }: Props) {
  const classes = ["page-row", rule === "single" && "is-ruled", rule === "double" && "is-double", className]
    .filter(Boolean)
    .join(" ");

  return <div className={classes}>{children}</div>;
}
