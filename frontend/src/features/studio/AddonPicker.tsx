/**
 * AddonPicker: the add-on part of the agent window. Every add-on is an
 * oval, filled when the agent has it; pointing at one says what it is.
 * Under them, for each add-on it has, a box for the owner's instructions:
 * how this agent should use it ("draft replies; never send"). They go into
 * its runs' AGENTS.md, under that add-on's guide. An add-on it still has
 * that was since removed from the studio is named in a quiet line: saving
 * the agent drops it.
 *
 * Used by AgentForm. Add-ons themselves are defined, and their guides
 * written, on the studio's add-ons page (AddonManager).
 */

import { WordChoice } from "../../components/WordChoice";
import type { Addon } from "../../types/addon";
import { summarizeAddon } from "./addonSummary";

interface Props {
  /** The agent's name, or "" while it's being added. */
  agent: string;
  addons: Addon[];
  picked: string[];
  instructions: Record<string, string>;
  onPick: (picked: string[]) => void;
  onInstruct: (instructions: Record<string, string>) => void;
}

export function AddonPicker({ agent, addons, picked, instructions, onPick, onInstruct }: Props) {
  const known = addons.filter((addon) => picked.includes(addon.name));
  const gone = picked.filter((name) => !addons.some((addon) => addon.name === name));
  const toggle = (name: string) => onPick(picked.includes(name) ? picked.filter((one) => one !== name) : [...picked, name]);

  return (
    <>
      <p className="word-list is-ovals" role="group" aria-label="add-ons">
        <span className="quiet">add-ons</span>
        {addons.map((addon) => (
          <WordChoice
            key={addon.name}
            label={addon.name}
            look="oval"
            hint={summarizeAddon(addon.guide)}
            active={picked.includes(addon.name)}
            onPick={() => toggle(addon.name)}
          />
        ))}
      </p>
      {gone.length > 0 && (
        <p className="quiet">Removed from the studio since, and dropped when you save: {gone.join(", ")}.</p>
      )}
      {known.map((addon) => (
        <label key={addon.name} className="addon-instructions">
          <span className="quiet">
            {addon.name}: how {agent || "this agent"} should use it
          </span>
          <textarea
            rows={2}
            placeholder="optional: what to do with it, or never do (its guide says what it is)"
            value={instructions[addon.name] ?? ""}
            onChange={(e) => onInstruct({ ...instructions, [addon.name]: e.target.value })}
          />
        </label>
      ))}
    </>
  );
}
