/**
 * TagNotesEditor: the owner's list of every tag, to write a description
 * (shown on the home page when the tag is selected) and set its importance:
 * key (listed first, in black), normal, or hidden (left off the tag line).
 */

import { useEffect, useState } from "react";
import { fetchTags, saveTagNotes } from "../../api/tagsApi";
import { WordChoice } from "../../components/WordChoice";
import type { Tag, TagImportance } from "../../types/entry";

const IMPORTANCE_LABELS: [TagImportance, string][] = [
  [1, "key"],
  [0, "normal"],
  [-1, "hidden"],
];

export function TagNotesEditor() {
  const [tags, setTags] = useState<Tag[]>([]);

  useEffect(() => {
    fetchTags().then(setTags).catch(console.error);
  }, []);

  if (tags.length === 0) return null;

  return (
    <section className="tag-notes">
      {tags.map((tag) => (
        <TagNotesRow key={tag.name} tag={tag} />
      ))}
    </section>
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
    <div className="tag-notes-row">
      <p className="word-list">
        <span>
          {tag.name} <span className="quiet">{tag.count}</span>
        </span>
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
        <span className="quiet">{status}</span>
      </p>
      <textarea
        rows={2}
        placeholder="what this tag means to me (saved when you click away)"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        onBlur={() => description !== tag.description && save({ description, importance })}
      />
    </div>
  );
}
