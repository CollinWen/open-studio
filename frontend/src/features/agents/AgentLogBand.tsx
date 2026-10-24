/**
 * AgentLogBand: the agent log's controls, in the same ControlBand as a
 * board's: a search over what agents wrote (and "clear" when anything is
 * picked), then a caret that opens
 *
 *   Agent   whose lines
 *   Board   which board they're about
 *   Type    plans, thoughts, findings, questions or status changes
 *
 * While those are closed, each pick shows beside the caret in a filled
 * oval; clicking one clears it. Used by AgentsPage. Every pick lives in
 * the URL (useLogFilters).
 */

import { ControlBand } from "../../components/ControlBand";
import { LabelRow } from "../../components/LabelRow";
import { SearchField } from "../../components/SearchField";
import { WordChoice } from "../../components/WordChoice";
import type { Agent, LogLineType } from "../../types/agent";
import type { Board } from "../../types/entry";
import { LINE_TYPES, type useLogFilters } from "./useLogFilters";

interface Props {
  agents: Agent[];
  boards: Board[];
  filters: ReturnType<typeof useLogFilters>;
}

const TYPE_WORDS: Record<LogLineType, string> = {
  plan: "plans",
  thought: "thoughts",
  finding: "findings",
  question: "questions",
  status: "status changes",
};

export function AgentLogBand({ agents, boards, filters }: Props) {
  const { agent, board, type, query, setFilter, clearFilters, hasFilters } = filters;

  /** One line of pick-one words, "all" first. */
  const choices = (name: "agent" | "board" | "type", all: string, options: [string, string][], current: string) => (
    <div className="word-list">
      <WordChoice label={all} active={!current} onPick={() => setFilter(name, "")} />
      {options.map(([value, label]) => (
        <WordChoice key={value} label={label} active={value === current} onPick={() => setFilter(name, value)} />
      ))}
    </div>
  );

  const picks: [string, "agent" | "board" | "type"][] = [
    [agent, "agent"],
    [board, "board"],
    [type && TYPE_WORDS[type], "type"],
  ];

  return (
    <ControlBand
      label="Search"
      rememberAs="log-filters-open"
      controls={
        <div className="browse-controls">
          <SearchField value={query} onSearch={(words) => setFilter("q", words)} placeholder="words in what they wrote" />
          {hasFilters && (
            <button type="button" className="clear-word" onClick={clearFilters}>
              clear ×
            </button>
          )}
        </div>
      }
      picked={
        <span className="word-list is-ovals">
          {picks.map(
            ([label, name]) =>
              label && <WordChoice key={name} label={label} look="oval" active onPick={() => setFilter(name, "")} />,
          )}
        </span>
      }
      more={
        <>
          <LabelRow label="Agent">
            {choices("agent", "all agents", agents.map((one) => [one.name, one.name]), agent)}
          </LabelRow>
          <LabelRow label="Board">
            {choices("board", "every board", boards.map((one) => [one.slug, one.slug]), board)}
          </LabelRow>
          <LabelRow label="Type">
            {choices("type", "everything", LINE_TYPES.map((one) => [one, TYPE_WORDS[one]]), type)}
          </LabelRow>
        </>
      }
    />
  );
}
