/**
 * EntryIndex: every entry (including private ones) as a plain list, with
 * its space, visibility and tags, and "edit" and "delete" beside each. Owner-only.
 */

import { Link } from "react-router-dom";
import { deleteEntry } from "../../api/entriesApi";
import type { Entry } from "../../types/entry";

interface Props {
  entries: Entry[];
  onEdit: (entry: Entry) => void;
  onChanged: () => void;
}

export function EntryIndex({ entries, onEdit, onChanged }: Props) {
  async function remove(entry: Entry) {
    if (!window.confirm(`Delete "${entry.title}"? This can't be undone.`)) return;
    await deleteEntry(entry.id);
    onChanged();
  }

  return (
    <section className="entry-index">
      {entries.map((entry) => (
        <p key={entry.id} className="word-list">
          <Link to={`/entry/${entry.id}`}>{entry.title}</Link>
          <span className="quiet">
            {entry.board} · {entry.visibility} · {entry.tags.join(", ") || "no tags"}
          </span>
          <button type="button" className="quiet" onClick={() => onEdit(entry)}>
            edit
          </button>
          <button type="button" className="quiet" onClick={() => remove(entry)}>
            delete
          </button>
        </p>
      ))}
    </section>
  );
}
