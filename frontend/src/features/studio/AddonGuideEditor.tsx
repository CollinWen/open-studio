/**
 * AddonGuideEditor: an add-on's guide, to write: what it is, what it's for,
 * how it works and what to watch, in markdown, as it goes into the AGENTS.md
 * of every run that has it. Above the text, what provides it and the
 * account it acts as. "save", a solid ink square, keeps it. How one agent
 * in particular should use it is written in that agent's window instead.
 *
 * Used by AddonManager, in a PaperWindow; a Composio add-on's tools are
 * listed under it (AddonToolList).
 */

import { useState } from "react";
import { updateAddonGuide } from "../../api/addonsApi";
import { LoadingWord } from "../../components/LoadingWord";
import type { Addon } from "../../types/addon";

interface Props {
  addon: Addon;
  onSaved: () => void;
  onCancel: () => void;
}

const SAVING = "saving";

export function AddonGuideEditor({ addon, onSaved, onCancel }: Props) {
  const [guide, setGuide] = useState(addon.guide);
  const [status, setStatus] = useState("");
  const provider =
    addon.kind === "sandbox"
      ? `the sandbox's ${addon.service}`
      : `Composio's ${addon.service}, ${addon.account ? `as ${addon.account}` : "not connected yet"}`;

  const save = () => {
    setStatus(SAVING);
    updateAddonGuide(addon.name, guide)
      .then(onSaved)
      .catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <form className="studio-form" onSubmit={(event) => (event.preventDefault(), save())}>
      <p className="quiet">
        {addon.name}: {provider}.
      </p>
      <textarea
        rows={10}
        aria-label="its guide"
        placeholder="**What it is:** … **Use it for:** … **How it works:** … **Watch:** …"
        value={guide}
        onChange={(e) => setGuide(e.target.value)}
      />
      <p className="word-list studio-form-actions">
        <button type="submit" className="square is-primary" disabled={status === SAVING}>
          save
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
        {status === SAVING ? <LoadingWord>{status}</LoadingWord> : <span className="quiet">{status}</span>}
      </p>
    </form>
  );
}
