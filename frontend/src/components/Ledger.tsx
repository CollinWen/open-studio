/**
 * Ledger: a list laid on the 12-column page grid, under a line of small
 * column names. Each column says how many grid columns it spans; the first
 * usually spans 3, so it hangs where labels do. Rows are LedgerRows, which
 * read the spans from here. The one way to show a list of things: entries
 * (rows view, studio), agents, the agent log, boards, tags.
 *
 * On phones the cells stack and the column names are hidden.
 * Looks: .ledger in global.css.
 */

import { createContext, type CSSProperties, type ReactNode } from "react";

export interface LedgerColumn {
  label: string;
  span: number;
}

export const LedgerSpans = createContext<number[]>([]);

interface Props {
  columns: LedgerColumn[];
  children: ReactNode;
}

export function Ledger({ columns, children }: Props) {
  return (
    <div className="ledger">
      <div className="ledger-row is-heading">
        {columns.map((column) => (
          <span key={column.label} className="ledger-cell" style={{ "--span": column.span } as CSSProperties}>
            {column.label}
          </span>
        ))}
      </div>
      <LedgerSpans.Provider value={columns.map((column) => column.span)}>{children}</LedgerSpans.Provider>
    </div>
  );
}
