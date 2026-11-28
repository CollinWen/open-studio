/**
 * AgentForm: add an agent or change one, in plain fields: its name (only
 * when adding; it can't change later), one line on what it's for, its
 * manifest (its standing job, written into every run's prompt; a starting
 * outline is offered while it's empty), the boards it may add to, the outside
 * tools its tokens may be given (web, code, github) and the skills it works
 * with, picked from the list. Boards, tools and skills are ovals, filled when on. The last line holds "add" (or "save"), a solid ink square,
 * and "cancel".
 *
 * Used by AgentManager, in a PaperWindow. Tokens are issued separately
 * (TokenForm); an agent has none of its own.
 */

import { useState } from "react";
import { addAgent, updateAgent } from "../../api/agentsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { WordChoice } from "../../components/WordChoice";
import { AGENT_SKILLS, OUTSIDE_TOOLS, type Agent, type AgentSkill, type OutsideTool } from "../../types/agent";
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

/** Shown in an empty manifest: the outline a manifest follows. */
const MANIFEST_OUTLINE = [
  "its manifest, the job every run starts from:",
  "Objective: what it is ultimately for.",
  "Focus: what it works on, and what it leaves alone.",
  "Tools: which it uses for what (the studio first, then the web, code or github).",
  "Hand back: what it adds and logs, and how much.",
].join("\n");

export function AgentForm({ agent, boards, onSaved, onCancel }: Props) {
  const [name, setName] = useState(agent?.name ?? "");
  const [description, setDescription] = useState(agent?.description ?? "");
  const [manifest, setManifest] = useState(agent?.manifest ?? "");
  const [onBoards, setOnBoards] = useState<string[]>(agent?.boards ?? []);
  const [tools, setTools] = useState<OutsideTool[]>(agent?.tools ?? []);
  // Skills no longer on the list are dropped on save, so the agent stays valid.
  const [skills, setSkills] = useState<AgentSkill[]>(
    (agent?.skills ?? []).filter((skill) => (AGENT_SKILLS as readonly string[]).includes(skill)),
  );
  const [status, setStatus] = useState("");

  const toggle = <T,>(list: T[], item: T) =>
    list.includes(item) ? list.filter((one) => one !== item) : [...list, item];

  const save = () => {
    const settings = {
      description: description.trim(),
      manifest: manifest.trim(),
      boards: onBoards,
      tools,
      skills,
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
      <input placeholder="what it's for, in one line" value={description} onChange={(e) => setDescription(e.target.value)} />
      <textarea
        rows={7}
        placeholder={MANIFEST_OUTLINE}
        aria-label="manifest"
        value={manifest}
        onChange={(e) => setManifest(e.target.value)}
      />
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
      <p className="word-list is-ovals" role="group" aria-label="skills">
        <span className="quiet">skills</span>
        {AGENT_SKILLS.map((skill) => (
          <WordChoice
            key={skill}
            label={skill}
            look="oval"
            active={skills.includes(skill)}
            onPick={() => setSkills(toggle(skills, skill))}
          />
        ))}
      </p>
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
