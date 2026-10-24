/**
 * AgentLog: what agents wrote about their work, newest first, as a Ledger.
 * Each line: when; then a short sentence saying who did what and where
 * ("scout found something on graphics") over what it wrote; then the entry
 * it's about, linked by name. Questions are for the owner, so they're set
 * in full ink.
 *
 * Used by AgentsPage ("log"), which loads the lines a page at a time.
 */

import { Link } from "react-router-dom";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { LogLine } from "../../types/agent";
import { boardPath } from "../grid/boardPath";
import { formatTimeAgo } from "./formatTimeAgo";

const COLUMNS = [
  { label: "when", span: 3 },
  { label: "what they wrote", span: 6 },
  { label: "entry", span: 3 },
];

/** Each kind of line, said as what the agent did. */
const SAID: Record<LogLine["type"], string> = {
  plan: "made a plan",
  thought: "had a thought",
  finding: "found something",
  question: "asked you",
  status: "changed its status",
};

export function AgentLog({ lines, narrowed }: { lines: LogLine[]; narrowed: boolean }) {
  if (lines.length === 0) return <p className="quiet">{narrowed ? "No lines match that." : "Nothing logged yet."}</p>;

  return (
    <Ledger columns={COLUMNS}>
      {lines.map((line) => (
        <LedgerRow
          key={line.id}
          className={`log-line is-${line.type}`}
          cells={[
            <span className="quiet">{formatTimeAgo(line.created_at)}</span>,
            <>
              <span className="log-line-said">
                <Link to={`/agents?agent=${line.agent}`}>{line.agent}</Link> {SAID[line.type]}
                {line.board && (
                  <>
                    {" on "}
                    <Link to={boardPath(line.board)}>{line.board}</Link>
                  </>
                )}
              </span>
              <span className="log-line-text">{line.text}</span>
            </>,
            line.entry_id && line.entry_title && (
              <Link to={`/entry/${line.entry_id}`} className="is-underlined">
                {line.entry_title}
              </Link>
            ),
          ]}
        />
      ))}
    </Ledger>
  );
}
