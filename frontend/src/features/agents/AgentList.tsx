/**
 * AgentList: every agent as one line of a Ledger: its name (a link to its
 * lines in the log), what it says it's doing now (with what it's for
 * underneath), the boards it's signed on to, and when it last called the
 * studio. A paused agent says so and fades.
 *
 * Used by AgentsPage ("who"). The owner's version, with controls, is
 * studio/AgentManager.tsx.
 */

import { Link } from "react-router-dom";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import type { Agent } from "../../types/agent";
import { boardPath } from "../grid/boardPath";
import { formatTimeAgo } from "./formatTimeAgo";

const COLUMNS = [
  { label: "agent", span: 3 },
  { label: "doing now", span: 5 },
  { label: "boards it works on", span: 2 },
  { label: "last seen", span: 2 },
];

export function AgentList({ agents }: { agents: Agent[] }) {
  if (agents.length === 0) return <p className="quiet">No agents yet.</p>;

  return (
    <Ledger columns={COLUMNS}>
      {agents.map((agent) => (
        <LedgerRow
          key={agent.name}
          className={agent.active ? undefined : "is-faded"}
          cells={[
            <Link to={`/agents?agent=${agent.name}`}>{agent.name}</Link>,
            <>
              {agent.active ? agent.status || <span className="quiet">no status yet</span> : "paused"}
              {agent.description && <span className="quiet ledger-note">{agent.description}</span>}
            </>,
            <span className="word-list quiet">
              {agent.boards.map((slug) => (
                <Link key={slug} to={boardPath(slug)}>
                  {slug}
                </Link>
              ))}
            </span>,
            <span className="quiet">{agent.last_seen_at ? formatTimeAgo(agent.last_seen_at) : "never seen"}</span>,
          ]}
        />
      ))}
    </Ledger>
  );
}
