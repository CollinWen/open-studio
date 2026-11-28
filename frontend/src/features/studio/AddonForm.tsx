/**
 * AddonForm: define an add-on, once, for every agent: the name agents and
 * runs know it by, what provides it (an outside service's toolkit on
 * Composio, or one of the sandbox's own tools: web, code, github), and
 * which toolkit or tool. "add", a solid ink square, saves it; its guide is
 * written from a template, which the window shows next, to change.
 *
 * Used by AddonManager, in a PaperWindow.
 */

import { useState } from "react";
import { addAddon } from "../../api/addonsApi";
import { LoadingWord } from "../../components/LoadingWord";
import { WordChoice } from "../../components/WordChoice";
import { ADDON_NAME, SANDBOX_SERVICES, TOOLKIT_NAME, type Addon, type AddonKind } from "../../types/addon";

interface Props {
  onAdded: (addon: Addon) => void;
  onCancel: () => void;
}

const ADDING = "adding";
const PROVIDERS: [AddonKind, string][] = [
  ["composio", "Composio"],
  ["sandbox", "the sandbox"],
];

export function AddonForm({ onAdded, onCancel }: Props) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState<AddonKind>("composio");
  const [service, setService] = useState("");
  const [status, setStatus] = useState("");
  const ready = ADDON_NAME.test(name) && (kind === "sandbox" ? service !== "" : TOOLKIT_NAME.test(service));

  const pickKind = (next: AddonKind) => {
    setKind(next);
    setService("");
  };

  const add = () => {
    setStatus(ADDING);
    addAddon({ name, kind, service })
      .then(onAdded)
      .catch((error) => setStatus(error instanceof Error ? error.message : String(error)));
  };

  return (
    <form className="studio-form" onSubmit={(event) => (event.preventDefault(), add())}>
      <input
        placeholder="name agents know it by (lowercase, e.g. email)"
        value={name}
        onChange={(e) => setName(e.target.value.trim().toLowerCase())}
      />
      <p className="word-list" role="group" aria-label="provided by">
        <span className="quiet">provided by</span>
        {PROVIDERS.map(([value, label]) => (
          <WordChoice key={value} label={label} active={kind === value} onPick={() => pickKind(value)} />
        ))}
      </p>
      {kind === "composio" ? (
        <input
          placeholder="its toolkit, as Composio names it (gmail, googledrive, notion, exa, …)"
          value={service}
          onChange={(e) => setService(e.target.value.trim().toLowerCase())}
        />
      ) : (
        <p className="word-list is-ovals" role="group" aria-label="the sandbox's tool">
          <span className="quiet">tool</span>
          {SANDBOX_SERVICES.map((tool) => (
            <WordChoice key={tool} label={tool} look="oval" active={service === tool} onPick={() => setService(tool)} />
          ))}
        </p>
      )}
      <p className="quiet">
        {kind === "composio"
          ? "Agents call its tools through the studio, as the account you connect next; Composio keeps the keys."
          : "Its harness provides it in the sandbox. Web, code and github are already here; another is the same tool with a guide of its own."}
      </p>
      <p className="word-list studio-form-actions">
        <button type="submit" className="square is-primary" disabled={!ready || status === ADDING}>
          add
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
        {status === ADDING ? <LoadingWord>{status}</LoadingWord> : <span className="quiet">{status}</span>}
      </p>
    </form>
  );
}
