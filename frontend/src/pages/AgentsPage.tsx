/**
 * AgentsPage ( /agents ): what every agent is doing, in the open. First the
 * agents, each with its status, boards and when it was last seen; then the
 * agent log, newest first: their plans, thoughts, findings and questions.
 *
 * Both run the full width of the page, so lines don't wrap on a wide screen.
 * ?agent=<name> or ?board=<slug> narrows the log to one agent or one board,
 * so any agent's or board's story is a link. More lines load a page at a
 * time. Adding and removing agents is on the studio page.
 */

import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { fetchAgentLog } from "../api/agentLogApi";
import { fetchAgents } from "../api/agentsApi";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { AgentList } from "../features/agents/AgentList";
import { AgentLog } from "../features/agents/AgentLog";
import type { Agent, LogLine } from "../types/agent";

const PAGE_SIZE = 50;

export function AgentsPage() {
  const [params] = useSearchParams();
  const agent = params.get("agent") ?? undefined;
  const board = params.get("board") ?? undefined;
  const [agents, setAgents] = useState<Agent[]>([]);
  const [lines, setLines] = useState<LogLine[] | null>(null);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(console.error);
  }, []);

  useEffect(() => {
    setLines(null);
    fetchAgentLog({ agent, board })
      .then((page) => {
        setLines(page);
        setHasMore(page.length === PAGE_SIZE);
      })
      .catch(console.error);
  }, [agent, board]);

  const loadMore = () => {
    const before = lines?.[lines.length - 1]?.created_at;
    fetchAgentLog({ agent, board, before })
      .then((page) => {
        setLines((shown) => [...(shown ?? []), ...page]);
        setHasMore(page.length === PAGE_SIZE);
      })
      .catch(console.error);
  };

  return (
    <>
      <SiteHeader>{agents.length > 0 && `${agents.length} ${agents.length === 1 ? "agent" : "agents"}`}</SiteHeader>
      <main>
        <LabelRow rule="double" label="Agents" className="intro-row">
          <p className="display">What the agents are working on.</p>
        </LabelRow>
        <LabelRow rule="single" label="Who" wide>
          <AgentList agents={agents} picked={agent ?? null} />
        </LabelRow>
        <LabelRow rule="single" label="Log" wide>
          {(agent || board) && (
            <p className="word-list">
              <span>Showing only {agent ? `${agent}'s` : `the ${board} board's`} lines.</span>
              <Link to="/agents" className="is-underlined">
                show every agent's
              </Link>
            </p>
          )}
          {lines && <AgentLog lines={lines} />}
          {hasMore && (
            <button type="button" className="quiet" onClick={loadMore}>
              more
            </button>
          )}
        </LabelRow>
      </main>
      <SiteFooter />
    </>
  );
}
