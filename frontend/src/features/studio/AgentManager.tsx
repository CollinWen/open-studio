/**
 * AgentManager: the owner's list of agents on the studio page. Add one (a
 * name and what it's for) and its token is shown once, with the line that
 * connects a Claude session to the studio; it's never shown again. For each
 * agent: the boards it may add to (an oval per board, filled when it's on),
 * pause / resume, a new token (the old one stops working), and remove.
 *
 * Used by StudioPage. What agents are doing is public at /agents.
 */

import { useCallback, useEffect, useState } from "react";
import { addAgent, fetchAgents, removeAgent, renewAgentToken, updateAgent } from "../../api/agentsApi";
import { fetchBoards, setBoardAgents } from "../../api/boardsApi";
import { WordChoice } from "../../components/WordChoice";
import type { Agent, AgentWithToken } from "../../types/agent";
import type { Board } from "../../types/entry";
import { HOME_BOARD } from "../grid/boardPath";

// Where agents connect: the backend's own address (in development, the backend on port 8000).
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function AgentManager() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [boards, setBoards] = useState<Board[]>([]);
  const [shownToken, setShownToken] = useState<AgentWithToken | null>(null);
  const [message, setMessage] = useState("");

  const reload = useCallback(() => {
    fetchAgents().then(setAgents).catch(console.error);
    fetchBoards().then(setBoards).catch(console.error);
  }, []);
  useEffect(reload, [reload]);

  /** Run an owner action, then show the result (or what went wrong) and reload. */
  const act = (action: () => Promise<unknown>) =>
    action()
      .then(() => setMessage(""))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(reload);

  const toggleBoard = (agent: Agent, board: Board) => {
    const on = board.agents.includes(agent.name);
    const next = on ? board.agents.filter((name) => name !== agent.name) : [...board.agents, agent.name];
    act(() => setBoardAgents(board.slug, next));
  };

  const otherBoards = boards.filter((board) => board.slug !== HOME_BOARD);

  return (
    <section className="agent-manager">
      <AddAgentForm onAdd={(fields) => act(() => addAgent(fields).then(setShownToken))} />
      {message && <p>{message}</p>}
      {shownToken && <TokenNotice shown={shownToken} onDone={() => setShownToken(null)} />}
      {agents.map((agent) => (
        <div key={agent.name} className="agent-manager-row">
          <p className="word-list">
            <span>{agent.name}</span>
            <WordChoice
              label={agent.active ? "pause" : "resume"}
              active={!agent.active}
              onPick={() => act(() => updateAgent(agent.name, { active: !agent.active }))}
            />
            <button type="button" className="quiet" onClick={() => act(() => renewAgentToken(agent.name).then(setShownToken))}>
              new token
            </button>
            <button
              type="button"
              className="quiet"
              onClick={() => window.confirm(`Remove ${agent.name}? What it added stays.`) && act(() => removeAgent(agent.name))}
            >
              remove
            </button>
            {agent.description && <span className="quiet">{agent.description}</span>}
          </p>
          <div className="word-list is-ovals">
            {otherBoards.map((board) => (
              <WordChoice
                key={board.slug}
                label={board.slug}
                look="oval"
                active={board.agents.includes(agent.name)}
                onPick={() => toggleBoard(agent, board)}
              />
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function AddAgentForm({ onAdd }: { onAdd: (fields: { name: string; description: string; boards: string[] }) => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  return (
    <form
      className="word-list agent-manager-add"
      onSubmit={(event) => {
        event.preventDefault();
        onAdd({ name: name.trim().toLowerCase(), description: description.trim(), boards: [] });
        setName("");
        setDescription("");
      }}
    >
      <input placeholder="new agent's name" value={name} onChange={(event) => setName(event.target.value)} />
      <input placeholder="what it's for" value={description} onChange={(event) => setDescription(event.target.value)} />
      <button type="submit" disabled={!name.trim()}>
        add agent
      </button>
    </form>
  );
}

function TokenNotice({ shown, onDone }: { shown: AgentWithToken; onDone: () => void }) {
  const command = `claude mcp add --transport http open-studio ${API_URL}/mcp --header "Authorization: Bearer ${shown.token}"`;
  return (
    <div className="agent-token-notice">
      <p>
        {shown.agent.name}'s token, shown only this once. Connect a Claude session with:
      </p>
      <pre>{command}</pre>
      <button type="button" onClick={onDone}>
        done
      </button>
    </div>
  );
}
