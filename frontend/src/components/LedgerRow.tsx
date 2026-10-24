/**
 * LedgerRow: one line of a Ledger, one cell per column. Given `to`, the
 * whole line is a link (its second cell underlines on hover). Extra classes
 * fade it (.is-faded) or let it rise in (.is-arriving, with --arrive-order).
 */

import { useContext, type CSSProperties, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { LedgerSpans } from "./Ledger";

interface Props {
  cells: ReactNode[];
  to?: string;
  className?: string;
  style?: CSSProperties;
}

export function LedgerRow({ cells, to, className, style }: Props) {
  const spans = useContext(LedgerSpans);
  const classes = ["ledger-row", to && "is-link", className].filter(Boolean).join(" ");
  const content = cells.map((cell, index) => (
    <div key={index} className="ledger-cell" style={{ "--span": spans[index] } as CSSProperties}>
      {cell}
    </div>
  ));

  return to ? (
    <Link to={to} className={classes} style={style}>
      {content}
    </Link>
  ) : (
    <div className={classes} style={style}>
      {content}
    </div>
  );
}
