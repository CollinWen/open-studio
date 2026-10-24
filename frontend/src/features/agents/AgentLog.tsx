/**
 * AgentLog: what agents wrote about their work, newest first, as a
 * timeline. Each line: when, then a short sentence saying who did what and
 * where ("scout found something on graphics"), then what it wrote, then
 * the entry it's about, linked by name. Questions are for the owner, so
 * they're set in full ink.
 *
 * Used by AgentsPage, which loads the lines a page at a time.
 */

import { Link } from "react-router-dom";
import type { LogLine } from "../../types/agent";
import { boardPath } from "../grid/boardPath";
import { formatTimeAgo } from "./formatTimeAgo";

/** Each kind of line, said as what the agent did. */
const SAID: Record<LogLine["type"], string> = {
  plan: "made a plan",
  thought: "had a thought",
  finding: "found something",
  question: "asked you",
  status: "changed its status",
};

export function AgentLog({ lines }: { lines: LogLine[] }) {
  if (lines.length === 0) return <p className="quiet">Nothing logged yet.</p>;

  return (
    <div className="agent-log">
      {lines.map((line) => (
        <div key={line.id} className={`agent-log-line is-${line.type}`}>
          <span className="quiet">{formatTimeAgo(line.created_at)}</span>
          <div>
            <p className="agent-log-meta">
              <Link to={`?agent=${line.agent}`}>{line.agent}</Link> {SAID[line.type]}
              {line.board && (
                <>
                  {" on "}
                  <Link to={boardPath(line.board)}>{line.board}</Link>
                </>
              )}
            </p>
            <p className="agent-log-text">{line.text}</p>
            {line.entry_id && line.entry_title && (
              <p className="agent-log-entry">
                <span className="quiet">entry: </span>
                <Link to={`/entry/${line.entry_id}`} className="is-underlined">
                  {line.entry_title}
                </Link>
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
