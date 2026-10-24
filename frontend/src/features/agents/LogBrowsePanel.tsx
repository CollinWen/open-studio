/**
 * LogBrowsePanel: every way to move around the agent log, in the same shape
 * as a board's browse panel:
 *
 *   Agent   whose lines (larger words, the current one in accent)
 *   Then, on the shaded band:
 *   Search  words in what they wrote, then "clear" when anything is picked
 *   Board   which board the lines are about
 *   Type    plans, thoughts, findings, questions or status changes
 *
 * Used by AgentsPage. Every pick lives in the URL (useLogFilters).
 */

import { useEffect, useState } from "react";
import { LabelRow } from "../../components/LabelRow";
import { WordChoice } from "../../components/WordChoice";
import type { Agent, LogLineType } from "../../types/agent";
import type { Board } from "../../types/entry";
import { LINE_TYPES, type useLogFilters } from "./useLogFilters";

interface Props {
  agents: Agent[];
  boards: Board[];
  filters: ReturnType<typeof useLogFilters>;
}

const SEARCH_DELAY_MS = 300;
const TYPE_WORDS: Record<LogLineType, string> = {
  plan: "plans",
  thought: "thoughts",
  finding: "findings",
  question: "questions",
  status: "status changes",
};

export function LogBrowsePanel({ agents, boards, filters }: Props) {
  const { agent, board, type, query, setFilter, clearFilters, hasFilters } = filters;
  const [typed, setTyped] = useState(query);

  // Follow the URL when it changes from outside (back button, a link, "clear").
  useEffect(() => {
    setTyped((current) => (current.trim() === query ? current : query));
  }, [query]);

  // Wait for a pause in typing before searching, so each keystroke isn't a request.
  useEffect(() => {
    if (typed.trim() === query) return;
    const timer = setTimeout(() => setFilter("q", typed.trim()), SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [typed, query, setFilter]);

  return (
    <section className="browse-panel">
      <LabelRow rule="single" label="Agent" className="space-row">
        <nav className="word-list board-line" aria-label="Agents">
          <WordChoice label="all" active={!agent} onPick={() => setFilter("agent", "")} />
          {agents.map((candidate) => (
            <WordChoice
              key={candidate.name}
              label={candidate.name}
              active={candidate.name === agent}
              onPick={() => setFilter("agent", candidate.name)}
            />
          ))}
        </nav>
      </LabelRow>
      <div className="browse-controls-band">
        <LabelRow label="Search">
          <div className="browse-controls">
            <input
              className="search-field"
              type="search"
              placeholder="words in what they wrote"
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
            />
            {hasFilters && (
              <button type="button" className="clear-word" onClick={clearFilters}>
                clear ×
              </button>
            )}
          </div>
        </LabelRow>
        <LabelRow label="Board">
          <div className="word-list">
            <WordChoice label="every board" active={!board} onPick={() => setFilter("board", "")} />
            {boards.map((candidate) => (
              <WordChoice
                key={candidate.slug}
                label={candidate.slug}
                active={candidate.slug === board}
                onPick={() => setFilter("board", candidate.slug)}
              />
            ))}
          </div>
        </LabelRow>
        <LabelRow label="Type">
          <div className="word-list">
            <WordChoice label="everything" active={!type} onPick={() => setFilter("type", "")} />
            {LINE_TYPES.map((candidate) => (
              <WordChoice
                key={candidate}
                label={TYPE_WORDS[candidate]}
                active={candidate === type}
                onPick={() => setFilter("type", candidate)}
              />
            ))}
          </div>
        </LabelRow>
      </div>
    </section>
  );
}
