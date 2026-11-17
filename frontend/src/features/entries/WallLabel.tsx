/**
 * WallLabel: the museum-style placard for an entry, every fact about it in
 * one place: (for the owner) "edit" and who sees it, then a stack of small
 * captions over their values: Board (linking back to it), Kind, Date,
 * Source (SourceLink), Added by when an agent added it, and Tags.
 *
 * Used by EntryPage, which sets it in the narrow column beside the entry's
 * notes and pictures (.entry-aside in global.css).
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { boardPath } from "../grid/boardPath";
import type { Entry } from "../../types/entry";
import { EntryTags } from "./EntryTags";
import { formatDate } from "./formatDate";
import { SourceLink } from "./SourceLink";

export function WallLabel({ entry, ownerActions }: { entry: Entry; ownerActions?: ReactNode }) {
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
  if (entry.source_name || entry.source_url) {
    facts.push(["Source", <SourceLink name={entry.source_name} url={entry.source_url} />]);
  }
  if (entry.added_by !== "owner") {
    facts.push([
      "Added by",
      <>
        {entry.added_by.replace("agent:", "")} <span className="quiet">(agent)</span>
      </>,
    ]);
  }
  if (entry.tags.length > 0) facts.push(["Tags", <EntryTags tags={entry.tags} board={entry.board} />]);

  return (
    <>
      {ownerActions}
      <dl className="fact-list">
        {facts.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </>
  );
}
