/**
 * AgentList: every agent as one line of a ledger, under a line of column
 * names: its name (a link that narrows the log below to it), what it says
 * it's doing now (with what it's for underneath), the boards it's signed
 * on to, and when it last called the studio. A paused agent says so.
 *
 * Used by AgentsPage. Looks: .ledger-row in global.css.
 */

import { Link } from "react-router-dom";
import type { Agent } from "../../types/agent";
import { boardPath } from "../grid/boardPath";
import { formatTimeAgo } from "./formatTimeAgo";

interface Props {
  agents: Agent[];
  picked: string | null;
}

export function AgentList({ agents, picked }: Props) {
  if (agents.length === 0) return <p className="quiet">No agents yet.</p>;

  return (
    <div className="agent-ledger">
      <div className="ledger-row is-heading">
        <span>agent</span>
        <span>doing now</span>
        <span>boards it works on</span>
        <span>last seen</span>
      </div>
      {agents.map((agent) => (
        <div key={agent.name} className={["ledger-row", !agent.active && "is-faded"].filter(Boolean).join(" ")}>
          <Link to={`?agent=${agent.name}`} className={agent.name === picked ? "is-active" : undefined}>
            {agent.name}
          </Link>
          <span>
            {agent.active ? agent.status || <span className="quiet">no status yet</span> : "paused"}
            {agent.description && <span className="quiet ledger-note">{agent.description}</span>}
          </span>
          <span className="word-list quiet">
            {agent.boards.map((slug) => (
              <Link key={slug} to={boardPath(slug)}>
                {slug}
              </Link>
            ))}
          </span>
          <span className="quiet">{agent.last_seen_at ? formatTimeAgo(agent.last_seen_at) : "never seen"}</span>
        </div>
      ))}
    </div>
  );
}
