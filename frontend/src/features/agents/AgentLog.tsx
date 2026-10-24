/**
 * AgentLog: what agents wrote about their work, newest first, as a
 * timeline. Each line: when (in the label column), then who, what kind of
 * line (plan, thought, finding, question, status) and which board, then
 * the text, then the entry it's about, linked by name. Questions are for
 * the owner, so they're set in full ink.
 *
 * Used by AgentsPage, which loads the lines a page at a time.
 */

import { Link } from "react-router-dom";
import type { LogLine } from "../../types/agent";
import { boardPath } from "../grid/boardPath";
import { formatTimeAgo } from "./formatTimeAgo";

export function AgentLog({ lines }: { lines: LogLine[] }) {
  if (lines.length === 0) return <p className="quiet">Nothing logged yet.</p>;

  return (
    <div className="agent-log">
      {lines.map((line) => (
        <div key={line.id} className={`agent-log-line is-${line.type}`}>
          <span className="quiet">{formatTimeAgo(line.created_at)}</span>
          <div>
            <p className="word-list agent-log-meta">
              <Link to={`?agent=${line.agent}`}>{line.agent}</Link>
              <span>{line.type}</span>
              {line.board && <Link to={boardPath(line.board)}>{line.board}</Link>}
            </p>
            <p className="agent-log-text">{line.text}</p>
            {line.entry_id && line.entry_title && (
              <Link to={`/entry/${line.entry_id}`} className="is-underlined">
                {line.entry_title}
              </Link>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
