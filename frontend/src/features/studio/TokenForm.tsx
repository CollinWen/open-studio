/**
 * TokenForm: issue an agent a token, which starts a run (one session). A
 * token is access only: pick the boards it may reach (all its boards, which
 * follows the agent's boards later, or some of them), the outside tools it
 * may use (all the agent was granted unless you pick) and how long it lasts
 * (20 minutes to 90 days; 4 hours unless you pick). What the agent is for is
 * its manifest (AgentForm); what to do this session you tell it in its harness.
 * "issue token", a solid ink square, sends it; the kit comes back to onIssued.
 *
 * Used by AgentManager, in a PaperWindow; TokenNotice then shows the token once.
 */

import { useState } from "react";
import { issueToken } from "../../api/runsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { WordChoice } from "../../components/WordChoice";
import type { Agent, OutsideTool } from "../../types/agent";
import { ALL_BOARDS, type RunKit } from "../../types/run";
import { TOKEN_LENGTHS, DEFAULT_TOKEN_LENGTH } from "./tokenLengths";

interface Props {
  agent: Agent;
  onIssued: (kit: RunKit) => void;
  onCancel: () => void;
}

const ISSUING = "issuing";

export function TokenForm({ agent, onIssued, onCancel }: Props) {
  const [boards, setBoards] = useState<string[]>([ALL_BOARDS]);
  // null: every tool the agent was granted.
  const [tools, setTools] = useState<OutsideTool[] | null>(null);
  const [minutes, setMinutes] = useState(DEFAULT_TOKEN_LENGTH.minutes);
  const [status, setStatus] = useState("");

  const toggleBoard = (slug: string) => {
    const picked = boards.filter((one) => one !== ALL_BOARDS);
    const next = picked.includes(slug) ? picked.filter((one) => one !== slug) : [...picked, slug];
    setBoards(next.length ? next : [ALL_BOARDS]);
  };

  const toggleTool = (tool: OutsideTool) => {
    const current = tools ?? agent.tools;
    setTools(current.includes(tool) ? current.filter((one) => one !== tool) : [...current, tool]);
  };

  const issue = () => {
    setStatus(ISSUING);
    issueToken({ agent: agent.name, boards, minutes, ...(tools ? { tools } : {}) })
      .then(onIssued)
      .catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <form className="studio-form" onSubmit={(event) => (event.preventDefault(), issue())}>
      <p className="word-list is-ovals" role="group" aria-label="boards it may reach">
        <span className="quiet">boards</span>
        <WordChoice
          label="all its boards"
          look="oval"
          active={boards[0] === ALL_BOARDS}
          onPick={() => setBoards([ALL_BOARDS])}
        />
        {agent.boards.map((slug) => (
          <WordChoice
            key={slug}
            label={slug}
            look="oval"
            active={boards.includes(slug)}
            onPick={() => toggleBoard(slug)}
          />
        ))}
      </p>
      {agent.tools.length > 0 && (
        <p className="word-list is-ovals" role="group" aria-label="outside tools">
          <span className="quiet">outside tools</span>
          <WordChoice label="all it has" look="oval" active={tools === null} onPick={() => setTools(null)} />
          {agent.tools.map((tool) => (
            <WordChoice
              key={tool}
              label={tool}
              look="oval"
              active={!!tools?.includes(tool)}
              onPick={() => toggleTool(tool)}
            />
          ))}
        </p>
      )}
      <p className="word-list" role="group" aria-label="how long it lasts">
        <span className="quiet">lasts</span>
        {TOKEN_LENGTHS.map((length) => (
          <WordChoice
            key={length.minutes}
            label={length.label}
            active={minutes === length.minutes}
            onPick={() => setMinutes(length.minutes)}
          />
        ))}
      </p>
      <p className="word-list studio-form-actions">
        <button type="submit" className="square is-primary" disabled={status === ISSUING}>
          issue token
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
        {status === ISSUING ? <LoadingWord>{status}</LoadingWord> : <span className="quiet">{status}</span>}
      </p>
    </form>
  );
}
