/**
 * AgentManager: the studio's "agents". The control band adds one (a name,
 * what it's for, a plus); its token is then shown once in the band, with
 * the line that connects a Claude session, and never again. Below, a Ledger
 * of every agent: the boards it may add to (an oval per board, filled when
 * it's on), when it was last seen, and pause / resume, a new token (the old
 * one stops working) and remove.
 *
 * Used by StudioPage, which loads the agents and boards. What agents are
 * doing is public at /agents.
 */

import { useState } from "react";
import { addAgent, removeAgent, renewAgentToken, updateAgent } from "../../api/agentsApi";
import { setBoardAgents } from "../../api/boardsApi";
import { ControlBand } from "../../components/ControlBand";
import { Icon } from "../../components/Icon";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { WordChoice } from "../../components/WordChoice";
import type { Agent, AgentWithToken } from "../../types/agent";
import type { Board } from "../../types/entry";
import { formatTimeAgo } from "../agents/formatTimeAgo";
import { HOME_BOARD } from "../grid/boardPath";

// Where agents connect: the backend's own address (in development, the backend on port 8000).
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Props {
  agents: Agent[];
  boards: Board[];
  onChanged: () => void;
}

const COLUMNS = [
  { label: "agent", span: 3 },
  { label: "boards it may add to", span: 5 },
  { label: "last seen", span: 2 },
  { label: "manage", span: 2 },
];

export function AgentManager({ agents, boards, onChanged }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [shownToken, setShownToken] = useState<AgentWithToken | null>(null);
  const [message, setMessage] = useState("");

  /** Run an owner action, then show what went wrong (if anything) and reload. */
  const act = (action: () => Promise<unknown>) =>
    action()
      .then(() => setMessage(""))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(onChanged);

  const toggleBoard = (agent: Agent, board: Board) => {
    const on = board.agents.includes(agent.name);
    const next = on ? board.agents.filter((one) => one !== agent.name) : [...board.agents, agent.name];
    act(() => setBoardAgents(board.slug, next));
  };

  const otherBoards = boards.filter((board) => board.slug !== HOME_BOARD);

  return (
    <>
      <ControlBand
        label="Add"
        controls={
          <form
            className="browse-controls"
            onSubmit={(event) => {
              event.preventDefault();
              act(() =>
                addAgent({ name: name.trim().toLowerCase(), description: description.trim(), boards: [] }).then(
                  setShownToken,
                ),
              );
              setName("");
              setDescription("");
            }}
          >
            <input placeholder="name" value={name} onChange={(event) => setName(event.target.value)} />
            <input
              className="is-long"
              placeholder="what it's for"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
            <button type="submit" className="icon-button" aria-label="add agent" disabled={!name.trim()}>
              <Icon name="plus" />
            </button>
            {message && <span>{message}</span>}
          </form>
        }
      >
        {shownToken && (
          <LabelRow label="Token">
            <TokenNotice shown={shownToken} onDone={() => setShownToken(null)} />
          </LabelRow>
        )}
      </ControlBand>
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {agents.map((agent) => (
            <LedgerRow
              key={agent.name}
              className={agent.active ? undefined : "is-faded"}
              cells={[
                <>
                  {agent.name}
                  {agent.description && <span className="quiet ledger-note">{agent.description}</span>}
                </>,
                <span className="word-list is-ovals">
                  {otherBoards.map((board) => (
                    <WordChoice
                      key={board.slug}
                      label={board.slug}
                      look="oval"
                      active={board.agents.includes(agent.name)}
                      onPick={() => toggleBoard(agent, board)}
                    />
                  ))}
                </span>,
                <span className="quiet">{agent.last_seen_at ? formatTimeAgo(agent.last_seen_at) : "never seen"}</span>,
                <span className="word-list">
                  <WordChoice
                    label={agent.active ? "pause" : "resume"}
                    active={!agent.active}
                    onPick={() => act(() => updateAgent(agent.name, { active: !agent.active }))}
                  />
                  <button
                    type="button"
                    className="quiet"
                    onClick={() => act(() => renewAgentToken(agent.name).then(setShownToken))}
                  >
                    new token
                  </button>
                  <button
                    type="button"
                    className="quiet"
                    onClick={() =>
                      window.confirm(`Remove ${agent.name}? What it added stays.`) && act(() => removeAgent(agent.name))
                    }
                  >
                    remove
                  </button>
                </span>,
              ]}
            />
          ))}
        </Ledger>
      </LabelRow>
    </>
  );
}

function TokenNotice({ shown, onDone }: { shown: AgentWithToken; onDone: () => void }) {
  const command = `claude mcp add --transport http open-studio ${API_URL}/mcp --header "Authorization: Bearer ${shown.token}"`;
  return (
    <div className="agent-token-notice">
      <p>{shown.agent.name}'s token, shown only this once. Connect a Claude session with:</p>
      <pre>{command}</pre>
      <button type="button" onClick={onDone}>
        done
      </button>
    </div>
  );
}
