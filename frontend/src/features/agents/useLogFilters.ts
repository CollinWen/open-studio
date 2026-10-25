/**
 * useLogFilters: what the agent log on /agents is narrowed to, kept in the
 * URL so any view of it is a link: ?agent=, ?board=, ?type= (plan, thought,
 * finding, question, status) and ?q= (words in the text).
 *
 * Used by AgentsPage and AgentLogBand.
 */

import { useSearchParams } from "react-router-dom";
import type { LogLineType } from "../../types/agent";

export const LINE_TYPES: LogLineType[] = ["plan", "thought", "finding", "question", "status"];
const FILTERS = ["agent", "board", "type", "q"] as const;
type Filter = (typeof FILTERS)[number];

export function useLogFilters() {
  const [params, setParams] = useSearchParams();
  const agent = params.get("agent") ?? "";
  const board = params.get("board") ?? "";
  const typeParam = params.get("type") as LogLineType | null;
  const type: LogLineType | "" = typeParam && LINE_TYPES.includes(typeParam) ? typeParam : "";
  const query = params.get("q") ?? "";

  /** Set one filter (empty removes it). Typing replaces history instead of adding to it. */
  const setFilter = (name: Filter, value: string) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        if (value) next.set(name, value);
        else next.delete(name);
        return next;
      },
      { replace: name === "q" },
    );

  const clearFilters = () => setParams({});
  const hasFilters = Boolean(agent || board || type || query);

  return { agent, board, type, query, setFilter, clearFilters, hasFilters };
}
