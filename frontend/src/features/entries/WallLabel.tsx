/**
 * WallLabel: the museum-style placard for an entry. The title set large,
 * then one quiet line of its facts with no labels, because each says what
 * it is: the board it's on (linking back to it), kind, date, source and,
 * when an agent added it, who. For the owner, "edit" follows. Then the
 * "why it's here" description. It's all one part of the page, so space
 * separates these, not rules.
 *
 * Used by EntryPage. The rows come from components/PageRow.tsx.
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { PageRow } from "../../components/PageRow";
import { boardPath } from "../grid/boardPath";
import type { Entry } from "../../types/entry";
import { formatDate } from "./formatDate";

export function WallLabel({ entry, ownerActions }: { entry: Entry; ownerActions?: ReactNode }) {
  return (
    <>
      <PageRow rule="double" className="intro-row">
        <h1 className="display">{entry.title}</h1>
      </PageRow>
      <PageRow>
        <p className="word-list quiet wall-facts">
          <Link to={boardPath(entry.board)} className="is-underlined">
            {entry.board}
          </Link>
          <span>{entry.kind}</span>
          <span>{formatDate(entry.occurred_at)}</span>
          {entry.source_url ? (
            <a href={entry.source_url} target="_blank" rel="noreferrer" className="is-underlined">
              {entry.source_name || "source"}
            </a>
          ) : (
            entry.source_name && <span>{entry.source_name}</span>
          )}
          {entry.added_by !== "owner" && <span>added by {entry.added_by.replace("agent:", "")}, an agent</span>}
        </p>
        {ownerActions}
      </PageRow>
      {entry.description && (
        <PageRow className="is-spaced">
          <div className="prose">
            {entry.description.split(/\n{2,}/).map((paragraph, index) => (
              <p key={index}>{paragraph}</p>
            ))}
          </div>
        </PageRow>
      )}
    </>
  );
}
