/**
 * AgentsPage ( /agents, /agents/who ): what the agents are doing, in the
 * open, laid out like every page: an intro, a section line, controls, then
 * one list.
 *
 *   log   ( /agents )      the agent log, newest first: their plans,
 *                          thoughts, findings and questions, with a search
 *                          and, behind a caret, agent / board / type
 *                          (AgentLogBand; every pick in the URL)
 *   who   ( /agents/who )  every agent: what it's doing now, its boards,
 *                          when it was last seen
 *
 * More lines load a page at a time. Adding and removing agents is in the
 * studio (/studio/agents).
 */

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchAgentLog } from "../api/agentLogApi";
import { fetchAgents } from "../api/agentsApi";
import { fetchBoards } from "../api/boardsApi";
import { LabelRow } from "../components/LabelRow";
import { SectionLine } from "../components/SectionLine";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { AgentList } from "../features/agents/AgentList";
import { AgentLog } from "../features/agents/AgentLog";
import { AgentLogBand } from "../features/agents/AgentLogBand";
import { useLogFilters } from "../features/agents/useLogFilters";
import type { Agent, LogLine } from "../types/agent";
import type { Board } from "../types/entry";

const PAGE_SIZE = 50;

export function AgentsPage() {
  const section = useParams().section === "who" ? "who" : "log";
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

  const sections = [
    { key: "log", label: "log", to: "/agents" },
    { key: "who", label: "who", to: "/agents/who", count: agents.length || undefined },
  ];

  return (
    <>
      <SiteHeader>{agents.length > 0 && `${agents.length} ${agents.length === 1 ? "agent" : "agents"}`}</SiteHeader>
      <main>
        <LabelRow rule="double" label="Agents" className="intro-row">
          <p className="display">What the agents are working on.</p>
        </LabelRow>
        <SectionLine label="Show" sections={sections} current={section} />
        {section === "log" && (
          <>
            <AgentLogBand agents={agents} boards={boards} filters={filters} />
            <LabelRow wide>
              {lines && <AgentLog lines={lines} narrowed={filters.hasFilters} />}
              {hasMore && (
                <button type="button" className="quiet" onClick={loadMore}>
                  more
                </button>
              )}
            </LabelRow>
          </>
        )}
        {section === "who" && (
          <LabelRow wide>
            <AgentList agents={agents} />
          </LabelRow>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
