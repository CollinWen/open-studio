/**
 * SectionLine: the first line of a page's controls, naming what you're
 * looking at, as a line of larger words: the boards on a board page, "log"
 * and "who" on the agents page, the studio's lists. The current one sits on
 * a solid square of the accent, in paper-colored type; a count, when given,
 * follows in brackets. Each word is a link, so every section has its own
 * address. `label` is not shown; screen readers hear it as the line's name.
 *
 * It starts a section with a single rule above, or none when it's the
 * first thing under the header's rule (a board page, which has no intro).
 * Anything passed as children sits under the words (a board's agents).
 * Used by BrowsePanel, AgentsPage and StudioPage. Looks: .section-line.
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";

export interface Section {
  key: string;
  label: string;
  to: string;
  count?: number;
}

interface Props {
  label: string;
  sections: Section[];
  current: string;
  rule?: "single" | "none";
  children?: ReactNode;
}

export function SectionLine({ label, sections, current, rule = "single", children }: Props) {
  return (
    <LabelRow rule={rule === "none" ? undefined : rule} className="section-row">
      <nav className="word-list section-line" aria-label={label}>
        {sections.map((section) => (
          <Link
            key={section.key}
            to={section.to}
            className={section.key === current ? "square is-current" : "square quiet"}
            aria-current={section.key === current ? "page" : undefined}
          >
            {section.label}
            {section.count !== undefined && <span className="section-count"> ({section.count})</span>}
          </Link>
        ))}
      </nav>
      {children}
    </LabelRow>
  );
}
