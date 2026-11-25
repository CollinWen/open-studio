/**
 * ToolkitGrantsEditor: the toolkits part of the agent window. One line per
 * toolkit the agent may use through the studio (its name, how many tools,
 * the account it acts as, its pinned arguments) with "change" and "remove",
 * and "add toolkit". Changing or adding opens ToolkitGrantForm in place.
 * The grants are saved with the agent.
 *
 * Used by AgentForm.
 */

import { useState } from "react";
import { Icon } from "../../components/Icon";
import type { ToolkitGrant } from "../../types/toolkit";
import { ToolkitGrantForm } from "./ToolkitGrantForm";
import { formatPins } from "./toolkitPins";

interface Props {
  grants: Record<string, ToolkitGrant>;
  onChange: (grants: Record<string, ToolkitGrant>) => void;
}

// The toolkit open in the form: its name, NEW for one being added, or null.
const NEW = "";

export function ToolkitGrantsEditor({ grants, onChange }: Props) {
  const [open, setOpen] = useState<string | null>(null);

  const keep = (toolkit: string, grant: ToolkitGrant) => {
    onChange({ ...grants, [toolkit]: grant });
    setOpen(null);
  };
  const remove = (toolkit: string) => {
    const { [toolkit]: _gone, ...rest } = grants;
    onChange(rest);
  };

  return (
    <>
      <p className="word-list">
        <span className="quiet">toolkits</span>
        {Object.keys(grants).length === 0 && <span className="quiet">none: GitHub, Exa and others, through Composio</span>}
        {open === null && (
          <button type="button" className="square quiet" onClick={() => setOpen(NEW)}>
            <Icon name="plus" /> add toolkit
          </button>
        )}
      </p>
      {Object.entries(grants).map(([toolkit, grant]) =>
        open === toolkit ? (
          <ToolkitGrantForm key={toolkit} toolkit={toolkit} grant={grant} onKeep={keep} onCancel={() => setOpen(null)} />
        ) : (
          <p key={toolkit} className="word-list">
            <span>{toolkit}</span>
            <span className="quiet">
              {grant.tools.length} {grant.tools.length === 1 ? "tool" : "tools"}
              {grant.connected_account && `, as ${grant.connected_account}`}
              {Object.keys(grant.pins).length > 0 && `, ${formatPins(grant.pins)}`}
            </span>
            <button type="button" className="quiet" onClick={() => setOpen(toolkit)}>
              change
            </button>
            <button type="button" className="quiet" onClick={() => remove(toolkit)}>
              remove
            </button>
          </p>
        ),
      )}
      {open === NEW && <ToolkitGrantForm toolkit={NEW} grant={null} onKeep={keep} onCancel={() => setOpen(null)} />}
    </>
  );
}
