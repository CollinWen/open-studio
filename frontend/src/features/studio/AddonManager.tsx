/**
 * AddonManager: the studio's "add-ons": everything an agent can be given
 * beyond the studio, each defined once for every agent. The control band
 * holds "add add-on". Below, a Ledger of every add-on: its name and what it
 * is (the first line of its guide), what provides it (the sandbox's own
 * tool, or a Composio toolkit), the account it acts as (with "connect",
 * which signs in on Composio's own page), the agents that use it, and
 * "guide" and "remove" (web, code and github stay).
 *
 * "add add-on" opens AddonForm in a window (?add-addon); once it's added,
 * the same window shows its guide, written from a template, to change
 * (?addon=<name>: AddonGuideEditor, and a Composio add-on's tools under it,
 * AddonToolList). Which agents use an add-on, and how, is set in each
 * agent's window; what an agent may do with a service's tools is set on
 * Composio, which checks every call.
 *
 * Used by StudioPage, which loads the add-ons and agents.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { removeAddon } from "../../api/addonsApi";
import { ControlBand } from "../../components/ControlBand";
import { Icon } from "../../components/Icon";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { PaperWindow } from "../../components/PaperWindow";
import type { Addon } from "../../types/addon";
import type { Agent } from "../../types/agent";
import { AddonForm } from "./AddonForm";
import { AddonGuideEditor } from "./AddonGuideEditor";
import { AddonToolList } from "./AddonToolList";
import { summarizeAddon } from "./addonSummary";
import { useAddonConnection } from "./useAddonConnection";
import { useAddonWindowParam } from "./useAddonWindowParam";

interface Props {
  addons: Addon[];
  agents: Agent[];
  onChanged: () => void;
}

const COLUMNS = [
  { label: "add-on", span: 4 },
  { label: "provided by", span: 2 },
  { label: "acts as", span: 2 },
  { label: "used by", span: 2 },
  { label: "manage", span: 2 },
];

export function AddonManager({ addons, agents, onChanged }: Props) {
  const windows = useAddonWindowParam();
  const connection = useAddonConnection(onChanged);
  const [message, setMessage] = useState("");
  // Just added: its window opens before the reloaded list has it.
  const [added, setAdded] = useState<Addon | null>(null);
  const open =
    addons.find((addon) => addon.name === windows.openAddon) ??
    (added && added.name === windows.openAddon ? added : null);

  const remove = (addon: Addon) =>
    window.confirm(`Remove ${addon.name}? Agents that have it lose it, and so do their runs.`) &&
    removeAddon(addon.name)
      .then(() => setMessage(""))
      .catch((error) => setMessage(error instanceof Error ? error.message : String(error)))
      .finally(onChanged);

  return (
    <>
      <ControlBand
        label="Add-ons"
        controls={
          <div className="browse-controls">
            <button type="button" className="square quiet" onClick={windows.openNewAddon}>
              <Icon name="plus" /> add add-on
            </button>
            {(message || connection.message) && <span>{message || connection.message}</span>}
          </div>
        }
      />
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {addons.map((addon) => {
            const users = agents.filter((agent) => agent.addons.includes(addon.name));
            return (
              <LedgerRow
                key={addon.name}
                cells={[
                  <>
                    {addon.name}
                    <span className="quiet ledger-note">{summarizeAddon(addon.guide)}</span>
                  </>,
                  <span className="quiet">
                    {addon.kind === "sandbox" ? "the sandbox" : "Composio"}
                    <span className="ledger-note">{addon.service}</span>
                  </span>,
                  addon.kind === "sandbox" ? (
                    <span className="quiet">nothing to connect</span>
                  ) : (
                    <span className="word-list">
                      <span className="quiet">{addon.account || "not connected"}</span>
                      <button type="button" onClick={() => connection.connect(addon.name)}>
                        {addon.account ? "reconnect" : "connect"}
                      </button>
                    </span>
                  ),
                  users.length ? (
                    <span className="word-list">
                      {users.map((agent) => (
                        <Link key={agent.name} to={`/studio/agents?agent=${encodeURIComponent(agent.name)}`}>
                          {agent.name}
                        </Link>
                      ))}
                    </span>
                  ) : (
                    <span className="quiet">no agent yet</span>
                  ),
                  <span className="word-list">
                    <button type="button" className="quiet" onClick={() => windows.openAddonGuide(addon.name)}>
                      guide
                    </button>
                    {!addon.built_in && (
                      <button type="button" className="quiet" onClick={() => remove(addon)}>
                        remove
                      </button>
                    )}
                  </span>,
                ]}
              />
            );
          })}
        </Ledger>
      </LabelRow>

      <PaperWindow
        open={windows.isAddingAddon || open !== null}
        title={open ? `${open.name}: its guide, in every AGENTS.md that has it` : "Add an add-on"}
        onClose={windows.closeAddonWindows}
      >
        {windows.isAddingAddon && (
          <AddonForm
            onAdded={(addon) => {
              setAdded(addon);
              onChanged();
              windows.openAddonGuide(addon.name);
            }}
            onCancel={windows.closeAddonWindows}
          />
        )}
        {open && (
          <>
            <AddonGuideEditor
              key={open.name}
              addon={open}
              onSaved={() => {
                onChanged();
                windows.closeAddonWindows();
              }}
              onCancel={windows.closeAddonWindows}
            />
            {open.kind === "composio" && <AddonToolList key={`${open.name}-tools`} addon={open} />}
          </>
        )}
      </PaperWindow>
    </>
  );
}
