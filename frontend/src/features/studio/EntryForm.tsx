/**
 * EntryForm: write a new entry or edit an existing one. Plain text fields,
 * no boxes. Leaving tags blank asks the backend to suggest them.
 *
 * A new entry asks only for the essentials (a link, a title, why it's here,
 * who sees it); kind, date, source, tags and pictures sit behind "more",
 * summed up in one quiet line. Editing shows everything.
 * Pasting a link at the top fills in whatever fields are still empty and adds
 * the link's pictures to the media list (see LinkCaptureField).
 *
 * Saving can take a few seconds: the backend generates tags and an
 * embedding before it replies.
 */

import { useState } from "react";
import { createEntry, updateEntry } from "../../api/entriesApi";
import { WordChoice } from "../../components/WordChoice";
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
  const [showMore, setShowMore] = useState(editing !== null);

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
      <LinkCaptureField onCaptured={applyCaptured} autoFocus={!editing} />
      <input placeholder="title" value={draft.title} onChange={(e) => set("title", e.target.value)} required />
      <textarea
        placeholder="why it's here"
        rows={4}
        value={draft.description}
        onChange={(e) => set("description", e.target.value)}
      />

      {!showMore && (
        <p className="word-list">
          <button type="button" onClick={() => setShowMore(true)}>
            more
          </button>
          <span className="quiet">{summarize(draft, tagText)}</span>
        </p>
      )}
      {showMore && (
        <>
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
          <input
            placeholder="source name"
            value={draft.source_name}
            onChange={(e) => set("source_name", e.target.value)}
          />
          <input placeholder="source url" value={draft.source_url} onChange={(e) => set("source_url", e.target.value)} />
          <input
            placeholder="tags, comma separated (blank = suggest)"
            value={tagText}
            onChange={(e) => setTagText(e.target.value)}
          />
          <MediaListEditor media={draft.media} onChange={(media) => set("media", media)} />
        </>
      )}

      <p className="word-list">
        {VISIBILITIES.map((visibility) => (
          <WordChoice
            key={visibility}
            label={visibility}
            active={draft.visibility === visibility}
            onPick={() => set("visibility", visibility)}
          />
        ))}
      </p>

      <p className="word-list">
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

/** One quiet line saying what's behind "more", so a pasted link's details are visible without opening it. */
function summarize(draft: EntryDraft, tagText: string): string {
  const pictures = draft.media.length;
  return [
    draft.kind,
    draft.occurred_at?.slice(0, 10),
    draft.source_name,
    pictures > 0 && `${pictures} ${pictures === 1 ? "picture" : "pictures"}`,
    tagText.trim() ? tagText : "tags suggested on save",
  ]
    .filter(Boolean)
    .join(" · ");
}

function parseTags(text: string): string[] {
  return text
    .split(",")
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean);
}
