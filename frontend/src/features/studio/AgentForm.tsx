/**
 * AgentForm: add an agent or change one, in plain fields: its name (only
 * when adding; it can't change later), one line on what it's for, its
 * manifest (its standing job, written into every run's prompt, in a
 * TextEditor; a starting outline is offered while it's empty), the boards it
 * may add to, the skills it works with, picked from the agent resources
 * (SkillPicker), and the add-ons it uses, each with the owner's instructions
 * for it (AddonPicker). Boards, skills and add-ons are ovals, filled when
 * on. The last line holds "add" (or "save"), a solid ink square, and
 * "cancel".
 *
 * Used by AgentManager, in a PaperWindow. Tokens are issued separately
 * (TokenForm); an agent has none of its own. What its runs get from all of
 * this is its AGENTS.md (AgentsMdView).
 */

import { useState } from "react";
import { addAgent, updateAgent } from "../../api/agentsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { TextEditor } from "../../components/TextEditor";
import { WordChoice } from "../../components/WordChoice";
import type { Addon } from "../../types/addon";
import type { Agent } from "../../types/agent";
import type { Board } from "../../types/entry";
import { HOME_BOARD } from "../grid/boardPath";
import { AddonPicker } from "./AddonPicker";
import { SkillPicker } from "./SkillPicker";

interface Props {
  /** The agent to change, or null to add one. */
  agent: Agent | null;
  boards: Board[];
  addons: Addon[];
  onSaved: () => void;
  onCancel: () => void;
}

const SAVING = "saving";

/** Shown in an empty manifest: the outline a manifest follows. */
const MANIFEST_OUTLINE = [
  "its manifest, the job every run starts from:",
  "Objective: what it is ultimately for.",
  "Focus: what it works on, and what it leaves alone.",
  "Tools: which it uses for what (the studio first, then its add-ons).",
  "Hand back: what it adds and logs, and how much.",
].join("\n");

export function AgentForm({ agent, boards, addons, onSaved, onCancel }: Props) {
  const [name, setName] = useState(agent?.name ?? "");
  const [description, setDescription] = useState(agent?.description ?? "");
  const [manifest, setManifest] = useState(agent?.manifest ?? "");
  const [onBoards, setOnBoards] = useState<string[]>(agent?.boards ?? []);
  const [skills, setSkills] = useState<string[]>(agent?.skills ?? []);
  const [picked, setPicked] = useState<string[]>(agent?.addons ?? []);
  const [instructions, setInstructions] = useState<Record<string, string>>(agent?.addon_instructions ?? {});
  const [status, setStatus] = useState("");

  const toggleBoard = (slug: string) =>
    setOnBoards(onBoards.includes(slug) ? onBoards.filter((one) => one !== slug) : [...onBoards, slug]);

  const save = () => {
    // An add-on removed from the studio since is dropped (AddonPicker says so).
    const kept = picked.filter((one) => addons.some((addon) => addon.name === one));
    const settings = {
      description: description.trim(),
      manifest: manifest.trim(),
      boards: onBoards,
      skills,
      addons: kept,
      addon_instructions: Object.fromEntries(kept.map((one) => [one, (instructions[one] ?? "").trim()])),
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
      <TextEditor
        rows={7}
        placeholder={MANIFEST_OUTLINE}
        label="manifest"
        value={manifest}
        onChange={setManifest}
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
              onPick={() => toggleBoard(board.slug)}
            />
          ))}
      </p>
      <SkillPicker picked={skills} onChange={setSkills} />
      <AddonPicker
        agent={agent?.name ?? name.trim().toLowerCase()}
        addons={addons}
        picked={picked}
        instructions={instructions}
        onPick={setPicked}
        onInstruct={setInstructions}
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
