/**
 * AgentsPage ( /agents ): what every agent is doing, in the open. First the
 * agents, each with its status, boards and when it was last seen; then a
 * browse panel like a board's (agent, search, board, type; LogBrowsePanel)
 * and the agent log under it, newest first: their plans, thoughts,
 * findings and questions.
 *
 * The list and the log run the full width of the page, so lines don't wrap
 * on a wide screen. Every pick is in the URL (useLogFilters), so any agent's
 * or board's story is a link. More lines load a page at a time. Adding and
 * removing agents is on the studio page.
 */

import { useEffect, useState } from "react";
import { fetchAgentLog } from "../api/agentLogApi";
import { fetchAgents } from "../api/agentsApi";
import { fetchBoards } from "../api/boardsApi";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { AgentList } from "../features/agents/AgentList";
import { AgentLog } from "../features/agents/AgentLog";
import { LogBrowsePanel } from "../features/agents/LogBrowsePanel";
import { useLogFilters } from "../features/agents/useLogFilters";
import type { Agent, LogLine } from "../types/agent";
import type { Board } from "../types/entry";

const PAGE_SIZE = 50;

export function AgentsPage() {
  const filters = useLogFilters();
  const { agent, board, type, query } = filters;
  const [agents, setAgents] = useState<Agent[]>([]);
  const [boards, setBoards] = useState<Board[]>([]);
  const [lines, setLines] = useState<LogLine[] | null>(null);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(console.error);
    fetchBoards().then(setBoards).catch(console.error);
  }, []);

  useEffect(() => {
    setLines(null);
    fetchAgentLog({ agent, board, type, q: query })
      .then((page) => {
        setLines(page);
        setHasMore(page.length === PAGE_SIZE);
      })
      .catch(console.error);
  }, [agent, board, type, query]);

  const loadMore = () => {
    const before = lines?.[lines.length - 1]?.created_at;
    fetchAgentLog({ agent, board, type, q: query, before })
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
        <LogBrowsePanel agents={agents} boards={boards} filters={filters} />
        <LabelRow wide>
          {lines && <AgentLog lines={lines} narrowed={filters.hasFilters} />}
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
