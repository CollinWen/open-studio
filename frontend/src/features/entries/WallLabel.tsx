/**
 * WallLabel: the museum-style placard for an entry.
 * Title, then "kind · date · source", then the "why it's here" description.
 */

import type { Entry } from "../../types/entry";
import { formatDate } from "./formatDate";

export function WallLabel({ entry }: { entry: Entry }) {
  const details = [entry.kind, formatDate(entry.occurred_at), entry.source_name].filter(Boolean);

  return (
    <div className="wall-label">
      <h1>{entry.title}</h1>
      <p className="quiet">
        {details.join(" · ")}
        {entry.source_url && (
          <>
            {" · "}
            <a href={entry.source_url} target="_blank" rel="noreferrer">
              source
            </a>
          </>
        )}
      </p>
      {entry.description.split(/\n{2,}/).map((paragraph, index) => (
        <p key={index}>{paragraph}</p>
      ))}
    </div>
  );
}

