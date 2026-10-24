/**
 * EntryIndex: the studio's "entries": every entry, private ones too, as a
 * Ledger (date, title, board, and its visibility with "edit" and "delete").
 * Above it, the shared control band: a search over titles and tags, and a
 * plus that opens the entry form (?add). Owner-only.
 *
 * Used by StudioPage, which loads the entries.
 */

import { Link } from "react-router-dom";
import { deleteEntry } from "../../api/entriesApi";
import { ControlBand } from "../../components/ControlBand";
import { Icon } from "../../components/Icon";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { SearchField } from "../../components/SearchField";
import type { Entry } from "../../types/entry";

interface Props {
  entries: Entry[];
  query: string;
  onSearch: (words: string) => void;
  onEdit: (entry: Entry) => void;
  onChanged: () => void;
}

const COLUMNS = [
  { label: "date", span: 3 },
  { label: "title", span: 5 },
  { label: "board", span: 2 },
  { label: "shown to", span: 2 },
];

export function EntryIndex({ entries, query, onSearch, onEdit, onChanged }: Props) {
  const words = query.toLowerCase();
  const shown = entries.filter(
    (entry) => entry.title.toLowerCase().includes(words) || entry.tags.some((tag) => tag.includes(words)),
  );

  async function remove(entry: Entry) {
    if (!window.confirm(`Delete "${entry.title}"? This can't be undone.`)) return;
    await deleteEntry(entry.id);
    onChanged();
  }

  return (
    <>
      <ControlBand
        label="Search"
        controls={
          <div className="browse-controls">
            <SearchField value={query} onSearch={onSearch} placeholder="titles and tags" />
            <Link to="?add" className="icon-button" aria-label="add an entry">
              <Icon name="plus" />
            </Link>
          </div>
        }
      />
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {shown.map((entry) => (
            <LedgerRow
              key={entry.id}
              cells={[
                <span className="quiet">{entry.occurred_at.slice(0, 10)}</span>,
                <Link to={`/entry/${entry.id}`}>{entry.title}</Link>,
                <span className="quiet">{entry.board}</span>,
                <span className="word-list">
                  <span className="quiet">{entry.visibility === "public" ? "everyone" : entry.visibility}</span>
                  <button type="button" className="quiet" onClick={() => onEdit(entry)}>
                    edit
                  </button>
                  <button type="button" className="quiet" onClick={() => remove(entry)}>
                    delete
                  </button>
                </span>,
              ]}
            />
          ))}
        </Ledger>
      </LabelRow>
    </>
  );
}
