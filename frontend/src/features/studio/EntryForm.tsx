/**
 * EntryForm: write a new entry or edit an existing one. Plain text fields,
 * no boxes. Leaving tags blank asks the backend to suggest them.
 *
 * Pasting a link at the top fills in whatever fields are still empty and adds
 * the link's pictures to the media list (see LinkCaptureField).
 *
 * Saving can take a few seconds: the backend generates tags and an
 * embedding before it replies.
 */

import { useState } from "react";
import { createEntry, updateEntry } from "../../api/entriesApi";
import type { CapturedLink, Entry, EntryDraft, Visibility } from "../../types/entry";
import { LinkCaptureField } from "./LinkCaptureField";
import { MediaListEditor } from "./MediaListEditor";

interface Props {
  editing: Entry | null;
  onSaved: () => void;
  onCancel: () => void;
}

const KINDS = ["note", "link", "project", "photo", "video", "book", "artwork", "sketch", "recipe", "post"];
const VISIBILITIES: Visibility[] = ["private", "unlisted", "public"];

export function EntryForm({ editing, onSaved, onCancel }: Props) {
  const [draft, setDraft] = useState<EntryDraft>(() => draftFrom(editing));
  const [tagText, setTagText] = useState(editing?.tags.join(", ") ?? "");
  const [status, setStatus] = useState("");

  const set = <K extends keyof EntryDraft>(field: K, value: EntryDraft[K]) =>
    setDraft((current) => ({ ...current, [field]: value }));

  /** Fill only the fields that are still empty, so a pasted link never overwrites my own words. */
  function applyCaptured(captured: CapturedLink) {
    setDraft((current) => ({
      ...current,
      title: current.title || captured.title,
      description: current.description || captured.description,
      kind: current.kind && current.kind !== "note" ? current.kind : captured.kind,
      source_name: current.source_name || captured.source_name,
      source_url: current.source_url || captured.source_url,
      occurred_at: current.occurred_at || captured.occurred_at,
      media: [...current.media, ...captured.media],
    }));
  }

  async function save() {
    setStatus("saving, suggesting tags…");
    const payload = { ...draft, tags: parseTags(tagText) };
    try {
      if (editing) await updateEntry(editing.id, payload);
      else await createEntry(payload);
      onSaved();
    } catch (error) {
      setStatus(`save failed: ${error instanceof Error ? error.message : error}`);
    }
  }

  return (
    <form className="entry-form" onSubmit={(event) => (event.preventDefault(), save())}>
      <p className="quiet">{editing ? "editing" : "new entry"}</p>
      <LinkCaptureField onCaptured={applyCaptured} />
      <input placeholder="title" value={draft.title} onChange={(e) => set("title", e.target.value)} required />
      <textarea
        placeholder="why it's here"
        rows={5}
        value={draft.description}
        onChange={(e) => set("description", e.target.value)}
      />
      <input placeholder="kind" list="kinds" value={draft.kind} onChange={(e) => set("kind", e.target.value)} />
      <datalist id="kinds">
        {KINDS.map((kind) => (
          <option key={kind} value={kind} />
        ))}
      </datalist>
      <input
        type="date"
        value={draft.occurred_at?.slice(0, 10) ?? ""}
        onChange={(e) => set("occurred_at", e.target.value || null)}
      />
      <input placeholder="source name" value={draft.source_name} onChange={(e) => set("source_name", e.target.value)} />
      <input placeholder="source url" value={draft.source_url} onChange={(e) => set("source_url", e.target.value)} />
      <input placeholder="tags, comma separated (blank = suggest)" value={tagText} onChange={(e) => setTagText(e.target.value)} />

      <MediaListEditor media={draft.media} onChange={(media) => set("media", media)} />

      <p>
        {VISIBILITIES.map((visibility) => (
          <button
            key={visibility}
            type="button"
            className={draft.visibility === visibility ? "is-active" : "quiet"}
            onClick={() => set("visibility", visibility)}
          >
            {visibility}
          </button>
        ))}
      </p>

      <p>
        <button type="submit">save</button>
        <button type="button" className="quiet" onClick={onCancel}>
          cancel
        </button>
        <span className="quiet">{status}</span>
      </p>
    </form>
  );
}

function draftFrom(entry: Entry | null): EntryDraft {
  return {
    title: entry?.title ?? "",
    description: entry?.description ?? "",
    kind: entry?.kind ?? "note",
    source_name: entry?.source_name ?? "",
    source_url: entry?.source_url ?? "",
    media: entry?.media ?? [],
    occurred_at: entry?.occurred_at ?? null,
    visibility: entry?.visibility ?? "private",
    tags: entry?.tags ?? [],
  };
}

function parseTags(text: string): string[] {
  return text
    .split(",")
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean);
}
