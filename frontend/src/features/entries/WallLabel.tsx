/**
 * WallLabel: the museum-style placard for an entry, as labeled rows.
 * The title set large, then Kind, Date and Source each on their own line,
 * then the "why it's here" description.
 *
 * Used by EntryPage. The rows come from components/LabelRow.tsx.
 */

import { LabelRow } from "../../components/LabelRow";
import type { Entry } from "../../types/entry";
import { formatDate } from "./formatDate";

export function WallLabel({ entry }: { entry: Entry }) {
  return (
    <>
      <LabelRow rule="double" label="Entry" className="intro-row">
        <h1 className="display">{entry.title}</h1>
      </LabelRow>
      <LabelRow rule="single" label="Kind">
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
