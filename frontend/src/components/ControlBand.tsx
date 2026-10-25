/**
 * ControlBand: the shaded band of controls under a SectionLine, edge to
 * edge, so tools read apart from the work. Its first line holds the main
 * controls (search, view, sort...). When there are more (`more`: tags and
 * time, or agent, board and type), a caret at the end of that line opens
 * and closes them; while closed, `picked` shows what is still narrowing the
 * view, so a closed band never hides a filter. `children` are lines that
 * are always shown (an "add" form).
 *
 * Whether it's open is remembered in this browser (`rememberAs`): it's how
 * you like the page, not what you're looking at, so it stays out of the URL.
 * Used by BrowsePanel, AgentsPage and StudioPage. Looks: .control-band
 * (the extra filters arrive as .control-band-more).
 */

import { useState, type ReactNode } from "react";
import { Icon } from "./Icon";
import { LabelRow } from "./LabelRow";

interface Props {
  label: string;
  controls: ReactNode;
  more?: ReactNode;
  picked?: ReactNode;
  rememberAs?: string;
  children?: ReactNode;
}

export function ControlBand({ label, controls, more, picked, rememberAs, children }: Props) {
  const [open, setOpen] = useState(() => readOpen(rememberAs));

  const toggle = () => {
    setOpen(!open);
    if (!rememberAs) return;
    try {
      localStorage.setItem(rememberAs, String(!open));
    } catch {
      // Storage can be blocked; the band still works, it just won't remember.
    }
  };

  return (
    <div className="control-band">
      <LabelRow label={label}>
        <div className="control-line">
          {controls}
          {more && (
            <button
              type="button"
              className="caret-toggle"
              aria-expanded={open}
              aria-label={open ? "fewer filters" : "more filters"}
              onClick={toggle}
            >
              <Icon name="caret" />
            </button>
          )}
          {more && !open && picked}
        </div>
      </LabelRow>
      {children}
      {more && open && <div className="control-band-more">{more}</div>}
    </div>
  );
}

function readOpen(key?: string): boolean {
  if (!key) return false;
  try {
    return localStorage.getItem(key) === "true";
  } catch {
    return false;
  }
}
