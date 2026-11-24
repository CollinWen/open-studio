/**
 * AgentManager: the studio's "agents". The control band holds "add agent"
 * and "agents.yaml" (every agent's setup as one file to download, no tokens).
 * Below, a Ledger of every agent: what it's for, the boards it may add to,
 * its outside tools and skills, when it was last seen, and "edit", "issue
 * token", its runs, pause / resume and remove.
 *
 * Adding or changing an agent opens AgentForm in a window (?add-agent,
 * ?agent=<name>); "issue token" opens TokenForm (?issue=<name>), and once a
 * token is issued the same window shows it once (TokenNotice). Closing that
 * window forgets the token. Agents have no token of their own: every token
 * is a run, listed under runs.
 *
 * Used by StudioPage, which loads the agents and boards. What agents are
 * doing is public at /agents.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { fetchAgentsYaml, removeAgent, updateAgent } from "../../api/agentsApi";
import { ControlBand } from "../../components/ControlBand";
import { Icon } from "../../components/Icon";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { PaperWindow } from "../../components/PaperWindow";
import { WordChoice } from "../../components/WordChoice";
import type { Agent } from "../../types/agent";
import type { Board } from "../../types/entry";
import type { RunKit } from "../../types/run";
import { formatTimeAgo } from "../agents/formatTimeAgo";
import { AgentForm } from "./AgentForm";
import { downloadText } from "./downloadText";
import { TokenForm } from "./TokenForm";
import { TokenNotice } from "./TokenNotice";
import { useAgentWindowParam } from "./useAgentWindowParam";

interface Props {
  agents: Agent[];
  boards: Board[];
  onChanged: () => void;
}

const COLUMNS = [
  { label: "agent", span: 3 },
  { label: "boards it may add to", span: 3 },
  { label: "tools · skills", span: 2 },
  { label: "last seen", span: 2 },
  { label: "manage", span: 2 },
];

export function AgentManager({ agents, boards, onChanged }: Props) {
  const windows = useAgentWindowParam();
  const [issued, setIssued] = useState<RunKit | null>(null);
  const [message, setMessage] = useState("");
  const editing = agents.find((agent) => agent.name === windows.editingAgent) ?? null;
  const issuingTo = agents.find((agent) => agent.name === windows.issuingFor) ?? null;

  /** Run an owner action, then show what went wrong (if anything) and reload. */
  const act = (action: () => Promise<unknown>) =>
    action()
      .then(() => setMessage(""))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(onChanged);

  const saved = () => {
    windows.closeAgentWindows();
    onChanged();
  };

  return (
    <>
      <ControlBand
        label="Agents"
        controls={
          <div className="browse-controls">
            <button type="button" className="square quiet" onClick={windows.openNewAgent}>
              <Icon name="plus" /> add agent
            </button>
            <button
              type="button"
              className="square quiet"
              onClick={() => act(() => fetchAgentsYaml().then((text) => downloadText("agents.yaml", text)))}
            >
              agents.yaml
            </button>
            {message && <span>{message}</span>}
          </div>
        }
      />
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
                <span className="quiet">{agent.boards.join(", ") || "none yet"}</span>,
                <span className="quiet">
                  {agent.tools.join(", ") || "no outside tools"}
                  {agent.skills.length > 0 && <span className="ledger-note">{agent.skills.join(", ")}</span>}
                </span>,
                <span className="quiet">{agent.last_seen_at ? formatTimeAgo(agent.last_seen_at) : "never seen"}</span>,
                <span className="word-list">
                  <button type="button" className="quiet" onClick={() => windows.openAgentEdit(agent.name)}>
                    edit
                  </button>
                  <button type="button" onClick={() => windows.openTokenIssue(agent.name)} disabled={!agent.active}>
                    issue token
                  </button>
                  <Link className="quiet" to={`/studio/runs?agent=${encodeURIComponent(agent.name)}`}>
                    runs
                  </Link>
                  <WordChoice
                    label={agent.active ? "pause" : "resume"}
                    active={!agent.active}
                    onPick={() => act(() => updateAgent(agent.name, { active: !agent.active }))}
                  />
                  <button
                    type="button"
                    className="quiet"
                    onClick={() =>
                      window.confirm(`Remove ${agent.name}? Its tokens stop working; what it added stays.`) &&
                      act(() => removeAgent(agent.name))
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

      <PaperWindow
        open={windows.isAddingAgent || editing !== null}
        title={editing ? `Change ${editing.name}` : "Add an agent"}
        onClose={windows.closeAgentWindows}
      >
        {(windows.isAddingAgent || editing) && (
          <AgentForm
            key={editing?.name ?? "new"}
            agent={editing}
            boards={boards}
            onSaved={saved}
            onCancel={windows.closeAgentWindows}
          />
        )}
      </PaperWindow>

      <PaperWindow
        open={issuingTo !== null}
        title={issued ? "Token, shown once" : `Issue ${issuingTo?.name ?? ""} a token`}
        onClose={windows.closeAgentWindows}
        onClosed={() => setIssued(null)}
      >
        {issued ? (
          <TokenNotice kit={issued} onDone={windows.closeAgentWindows} />
        ) : (
          issuingTo && (
            <TokenForm
              key={issuingTo.name}
              agent={issuingTo}
              onIssued={(kit) => {
                setIssued(kit);
                onChanged();
              }}
              onCancel={windows.closeAgentWindows}
            />
          )
        )}
      </PaperWindow>
    </>
  );
}
