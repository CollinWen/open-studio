/**
 * SectionLine: the first line of a page's controls, naming what you're
 * looking at, as a line of larger words: the boards on a board page, "log"
 * and "who" on the agents page, the studio's lists. The current one is
 * underlined in the accent; a count, when given, follows in brackets.
 * Each word is a link, so every section has its own address.
 *
 * `label` names the line for screen readers; it isn't shown.
 * Used by BrowsePanel, AgentsPage and StudioPage. Looks: .section-line.
 */

import { Link } from "react-router-dom";
import { PageRow } from "./PageRow";

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
}

export function SectionLine({ label, sections, current }: Props) {
  return (
    <PageRow rule="single" className="section-row">
      <nav className="word-list section-line" aria-label={label}>
        {sections.map((section) => (
          <Link
            key={section.key}
            to={section.to}
            className={section.key === current ? "is-active" : "quiet"}
            aria-current={section.key === current ? "page" : undefined}
          >
            {section.label}
            {section.count !== undefined && <span className="section-count"> ({section.count})</span>}
          </Link>
        ))}
      </nav>
    </PageRow>
  );
}
