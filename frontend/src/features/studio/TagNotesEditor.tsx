/**
 * TagNotesEditor: the studio's "tags": every tag as a Ledger line, to write
 * its description (shown as a board's intro when the tag is picked) and set
 * its importance: key (listed first, in black), normal, or hidden (left off
 * the tag line). The control band searches the tags by name.
 *
 * Used by StudioPage, which loads the tags.
 */

import { useState } from "react";
import { saveTagNotes } from "../../api/tagsApi";
import { ControlBand } from "../../components/ControlBand";
import { LabelRow } from "../../components/LabelRow";
import { Ledger } from "../../components/Ledger";
import { LedgerRow } from "../../components/LedgerRow";
import { SearchField } from "../../components/SearchField";
import { WordChoice } from "../../components/WordChoice";
import type { Tag, TagImportance } from "../../types/entry";

interface Props {
  tags: Tag[];
  query: string;
  onSearch: (words: string) => void;
}

const COLUMNS = [
  { label: "tag", span: 3 },
  { label: "what it means to me", span: 6 },
  { label: "importance", span: 3 },
];

const IMPORTANCE_LABELS: [TagImportance, string][] = [
  [1, "key"],
  [0, "normal"],
  [-1, "hidden"],
];

export function TagNotesEditor({ tags, query, onSearch }: Props) {
  const shown = tags.filter((tag) => tag.name.includes(query.toLowerCase()));

  return (
    <>
      <ControlBand label="Search" controls={<SearchField value={query} onSearch={onSearch} placeholder="tag names" />} />
      <LabelRow wide>
        <Ledger columns={COLUMNS}>
          {shown.map((tag) => (
            <TagNotesRow key={tag.name} tag={tag} />
          ))}
        </Ledger>
      </LabelRow>
    </>
  );
}

function TagNotesRow({ tag }: { tag: Tag }) {
  const [description, setDescription] = useState(tag.description);
  const [importance, setImportance] = useState<TagImportance>(tag.importance);
  const [status, setStatus] = useState("");

  async function save(next: { description: string; importance: TagImportance }) {
    setStatus("saving…");
    try {
      await saveTagNotes(tag.name, next);
      setStatus("saved");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  return (
    <LedgerRow
      cells={[
        <>
          {tag.name} <span className="quiet">{tag.count}</span>
          <span className="quiet ledger-note">{status}</span>
        </>,
        <textarea
          rows={1}
          placeholder="saved when you click away"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          onBlur={() => description !== tag.description && save({ description, importance })}
        />,
        <span className="word-list">
          {IMPORTANCE_LABELS.map(([value, label]) => (
            <WordChoice
              key={label}
              label={label}
              active={importance === value}
              onPick={() => {
                setImportance(value);
                save({ description, importance: value });
              }}
            />
          ))}
        </span>,
      ]}
    />
  );
}
