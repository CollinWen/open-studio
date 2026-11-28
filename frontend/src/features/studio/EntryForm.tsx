/**
 * EntryForm: write a new entry or edit an existing one. Plain text fields,
 * no boxes; "why it's here" is a TextEditor, so it takes markdown and links.
 * Leaving tags blank asks the backend to suggest them.
 *
 * A new entry asks only for the essentials (a title, a link, why it's here,
 * which space it goes in, who sees it, whether it's pinned first on its board); kind, date, source name, tags and pictures sit behind "more",
 * summed up in one quiet line. Editing shows everything.
 * The link is the entry's one source url; pasting one fills in whatever
 * fields are still empty and adds the link's pictures (see LinkCaptureField).
 *
 * The last line holds the buttons: "add" (or "save" when editing), a solid
 * ink square, and "cancel".
 *
 * Saving can take a few seconds: the backend generates tags and an
 * embedding before it replies.
 */

import { useState } from "react";
import { createEntry, updateEntry } from "../../api/entriesApi";
import { LoadingWord } from "../../components/LoadingWord";
import { TextEditor } from "../../components/TextEditor";
import { WordChoice } from "../../components/WordChoice";
import type { Board, CapturedLink, Entry, EntryDraft, Visibility } from "../../types/entry";
import { LinkCaptureField } from "./LinkCaptureField";
import { MediaListEditor } from "./MediaListEditor";

interface Props {
  editing: Entry | null;
  boards: Board[];
  /** Where a new entry goes unless another space is picked: the board you were looking at. */
  defaultBoard: string;
  onSaved: () => void;
  onCancel: () => void;
}

const SAVING = "saving, suggesting tags…";
const KINDS = ["note", "link", "project", "photo", "video", "book", "artwork", "sketch", "recipe", "post"];
const VISIBILITIES: Visibility[] = ["private", "unlisted", "public"];
const PIN_CHOICES = ["in order", "pinned"] as const;

export function EntryForm({ editing, boards, defaultBoard, onSaved, onCancel }: Props) {
  const [draft, setDraft] = useState<EntryDraft>(() => draftFrom(editing, defaultBoard));
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
      // The link field's own text, as the backend tidied it.
      source_url: captured.source_url || current.source_url,
      occurred_at: current.occurred_at || captured.occurred_at,
      media: [...current.media, ...captured.media],
    }));
  }

  async function save() {
    setStatus(SAVING);
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
    <form className="studio-form" onSubmit={(event) => (event.preventDefault(), save())}>
      <input
        autoFocus={!editing}
        placeholder="title"
        value={draft.title}
        onChange={(e) => set("title", e.target.value)}
        required
      />
      <LinkCaptureField
        url={draft.source_url}
        onChange={(url) => set("source_url", url)}
        onCaptured={applyCaptured}
      />
      <TextEditor
        placeholder="why it's here"
        rows={4}
        value={draft.description}
        onChange={(text) => set("description", text)}
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
          <input
            placeholder="tags, comma separated (blank = suggest)"
            value={tagText}
            onChange={(e) => setTagText(e.target.value)}
          />
          <MediaListEditor media={draft.media} onChange={(media) => set("media", media)} />
        </>
      )}

      {boards.length > 1 && (
        <p className="word-list" role="group" aria-label="board">
          {boards.map((board) => (
            <WordChoice
              key={board.slug}
              label={board.name.toLowerCase()}
              active={draft.board === board.slug}
              onPick={() => set("board", board.slug)}
            />
          ))}
        </p>
      )}

      <p className="word-list" role="group" aria-label="who sees it">
        {VISIBILITIES.map((visibility) => (
          <WordChoice
            key={visibility}
            label={visibility}
            active={draft.visibility === visibility}
            onPick={() => set("visibility", visibility)}
          />
        ))}
      </p>

      <p className="word-list" role="group" aria-label="pinned">
        {PIN_CHOICES.map((choice) => (
          <WordChoice
            key={choice}
            label={choice}
            active={draft.pinned === (choice === "pinned")}
            onPick={() => set("pinned", choice === "pinned")}
          />
        ))}
      </p>

      <p className="word-list studio-form-actions">
        <button type="submit" className="square is-primary" disabled={status === SAVING}>
          {editing ? "save" : "add"}
        </button>
        <button type="button" className="square quiet" onClick={onCancel}>
          cancel
        </button>
        {status === SAVING ? <LoadingWord>{status}</LoadingWord> : <span className="quiet">{status}</span>}
      </p>
    </form>
  );
}

function draftFrom(entry: Entry | null, defaultBoard: string): EntryDraft {
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
    board: entry?.board ?? defaultBoard,
    pinned: entry?.pinned ?? false,
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
