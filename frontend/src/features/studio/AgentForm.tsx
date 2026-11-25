/**
 * AgentForm: add an agent or change one, in plain fields: its name (only
 * when adding; it can't change later), what it's for, the boards it may add
 * to, the outside tools its tokens may be given (web, code, github) and the
 * skills it works with, by name, comma separated. Boards and tools are ovals,
 * filled when on. The last line holds "add" (or "save"), a solid ink square,
 * and "cancel".
 *
 * Used by AgentManager, in a PaperWindow. Tokens are issued separately
 * (TokenForm); an agent has none of its own.
 */

import { useState } from "react";
import { addAgent, updateAgent } from "../../api/agentsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { WordChoice } from "../../components/WordChoice";
import { OUTSIDE_TOOLS, type Agent, type OutsideTool } from "../../types/agent";
import type { Board } from "../../types/entry";
import { HOME_BOARD } from "../grid/boardPath";

interface Props {
  /** The agent to change, or null to add one. */
  agent: Agent | null;
  boards: Board[];
  onSaved: () => void;
  onCancel: () => void;
}

const SAVING = "saving";

export function AgentForm({ agent, boards, onSaved, onCancel }: Props) {
  const [name, setName] = useState(agent?.name ?? "");
  const [description, setDescription] = useState(agent?.description ?? "");
  const [onBoards, setOnBoards] = useState<string[]>(agent?.boards ?? []);
  const [tools, setTools] = useState<OutsideTool[]>(agent?.tools ?? []);
  const [skillText, setSkillText] = useState((agent?.skills ?? []).join(", "));
  const [status, setStatus] = useState("");

  const toggle = <T,>(list: T[], item: T) =>
    list.includes(item) ? list.filter((one) => one !== item) : [...list, item];

  const save = () => {
    const settings = {
      description: description.trim(),
      boards: onBoards,
      tools,
      skills: skillText
        .split(",")
        .map((skill) => skill.trim().toLowerCase())
        .filter(Boolean),
    };
    setStatus(SAVING);
    const saved = agent
      ? updateAgent(agent.name, settings)
      : addAgent({ name: name.trim().toLowerCase(), ...settings });
    saved.then(onSaved).catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <form className="studio-form" onSubmit={(event) => (event.preventDefault(), save())}>
      {!agent && (
        <input placeholder="name (lowercase, used in links)" value={name} onChange={(e) => setName(e.target.value)} />
      )}
      <input placeholder="what it's for" value={description} onChange={(e) => setDescription(e.target.value)} />
      <p className="word-list is-ovals" role="group" aria-label="boards it may add to">
        <span className="quiet">boards</span>
        {boards
          .filter((board) => board.slug !== HOME_BOARD)
          .map((board) => (
            <WordChoice
              key={board.slug}
              label={board.slug}
              look="oval"
              active={onBoards.includes(board.slug)}
              onPick={() => setOnBoards(toggle(onBoards, board.slug))}
            />
          ))}
      </p>
      <p className="word-list is-ovals" role="group" aria-label="outside tools">
        <span className="quiet">outside tools</span>
        {OUTSIDE_TOOLS.map((tool) => (
          <WordChoice
            key={tool}
            label={tool}
            look="oval"
            active={tools.includes(tool)}
            onPick={() => setTools(toggle(tools, tool))}
          />
        ))}
      </p>
      <input
        placeholder="skills, comma separated (e.g. gathering-sources, building)"
        value={skillText}
        onChange={(e) => setSkillText(e.target.value)}
      />
      <p className="word-list studio-form-actions">
        <button type="submit" className="square is-primary" disabled={status === SAVING || (!agent && !name.trim())}>
          {agent ? "save" : "add"}
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
        {status === SAVING ? <LoadingWord>{status}</LoadingWord> : <span className="quiet">{status}</span>}
      </p>
    </form>
  );
}
