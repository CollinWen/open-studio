/**
 * WallLabel: the museum-style placard for an entry, as labeled rows.
 * The title set large, then (for the owner) an Owner row with "edit" right
 * under it where it's easy to find, then Space (the board it's on, linking
 * back to it), Kind, Date, Source and, when an agent added it, Added by,
 * each on their own line, then the "why it's here" description.
 *
 * Used by EntryPage. The rows come from components/LabelRow.tsx.
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { LabelRow } from "../../components/LabelRow";
import { boardPath } from "../grid/boardPath";
import type { Entry } from "../../types/entry";
import { formatDate } from "./formatDate";

export function WallLabel({ entry, ownerActions }: { entry: Entry; ownerActions?: ReactNode }) {
  return (
    <>
      <LabelRow rule="double" label="Entry" className="intro-row">
        <h1 className="display">{entry.title}</h1>
      </LabelRow>
      {ownerActions && (
        <LabelRow rule="single" label="Owner">
          {ownerActions}
        </LabelRow>
      )}
      <LabelRow rule="single" label="Space">
        <Link to={boardPath(entry.board)} className="is-underlined">
          {entry.board}
        </Link>
      </LabelRow>
      <LabelRow label="Kind">
        {entry.kind}
      </LabelRow>
      <LabelRow label="Date">
        {formatDate(entry.occurred_at)}
      </LabelRow>
      {(entry.source_name || entry.source_url) && (
        <LabelRow label="Source">
          {entry.source_url ? (
            <a href={entry.source_url} target="_blank" rel="noreferrer" className="is-underlined">
              {entry.source_name || "link"}
            </a>
          ) : (
            entry.source_name
          )}
        </LabelRow>
      )}
      {entry.added_by !== "owner" && (
        <LabelRow label="Added by">
          {entry.added_by.replace("agent:", "")} <span className="quiet">(agent)</span>
        </LabelRow>
      )}
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
