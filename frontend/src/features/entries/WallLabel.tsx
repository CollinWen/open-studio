/**
 * WallLabel: the museum-style placard for an entry. The title set large,
 * then (for the owner) a line with "edit" right under it where it's easy to
 * find, then one row of facts across the page grid, each a small caption
 * over its value: Board (linking back to it), Kind, Date, Source and, when
 * an agent added it, Added by. Then the "why it's here" description.
 *
 * Used by EntryPage. The rows come from components/LabelRow.tsx; the facts
 * are laid out by .fact-row in global.css.
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { boardPath } from "../grid/boardPath";
import type { Entry } from "../../types/entry";
import { formatDate } from "./formatDate";

export function WallLabel({ entry, ownerActions }: { entry: Entry; ownerActions?: ReactNode }) {
  const source = entry.source_url ? (
    <a href={entry.source_url} target="_blank" rel="noreferrer" className="is-underlined">
      {entry.source_name || "link"}
    </a>
  ) : (
    entry.source_name
  );
  const facts: [string, ReactNode][] = [
    [
      "Board",
      <Link to={boardPath(entry.board)} className="is-underlined">
        {entry.board}
      </Link>,
    ],
    ["Kind", entry.kind],
    ["Date", formatDate(entry.occurred_at)],
  ];
  if (entry.source_name || entry.source_url) facts.push(["Source", source]);
  if (entry.added_by !== "owner") {
    facts.push([
      "Added by",
      <>
        {entry.added_by.replace("agent:", "")} <span className="quiet">(agent)</span>
      </>,
    ]);
  }

  return (
    <>
      <LabelRow rule="double" className="intro-row">
        <h1 className="display">{entry.title}</h1>
      </LabelRow>
      {ownerActions && <LabelRow rule="single">{ownerActions}</LabelRow>}
      <LabelRow rule="single">
        <dl className="fact-row">
          {facts.map(([label, value]) => (
            <div key={label} className="fact">
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </LabelRow>
      {entry.description && (
        <LabelRow rule="single" label="Notes">
          <div className="prose">
            {entry.description.split(/\n{2,}/).map((paragraph, index) => (
              <p key={index}>{paragraph}</p>
            ))}
          </div>
        </LabelRow>
      )}
    </>
  );
}
