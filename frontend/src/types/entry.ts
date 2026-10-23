/**
 * Data shapes shared across the frontend. These match the backend's
 * schemas.py files (entries, tags); change both together.
 */

export type Visibility = "private" | "unlisted" | "public";

/**
 * One picture or video in an entry. The first item in an entry's list is its cover.
 * image: shown with <img>.  video: a video file.  embed: a player in an iframe (YouTube, Drive video).
 * thumbnail_url: a still picture for the grid (needed for embeds; optional otherwise).
 */
export interface MediaItem {
  type: "image" | "video" | "embed";
  url: string;
  thumbnail_url: string;
  caption: string;
}

export interface Entry {
  id: string;
  title: string;
  description: string;
  kind: string;
  source_name: string;
  source_url: string;
  media: MediaItem[];
  occurred_at: string;
  created_at: string;
  updated_at: string;
  visibility: Visibility;
  tags: string[];
  /** "owner", or "agent:<name>" for an entry an agent added. */
  added_by: string;
  /** Slug of the board it's on; "home" is the owner's own collection. */
  board: string;
}

/** One page of entries from /api/entries/page. next_cursor is null on the last page. */
export interface EntryPage {
  entries: Entry[];
  next_cursor: string | null;
}

/** What the admin form sends. Empty tags means "suggest them for me". */
export type EntryDraft = Pick<
  Entry,
  "title" | "description" | "kind" | "source_name" | "source_url" | "media" | "visibility" | "tags"
> & { occurred_at: string | null };

/** A tag in use. importance: -1 hidden, 0 normal, 1 key (listed first, in black). */
export interface Tag {
  name: string;
  count: number;
  description: string;
  importance: TagImportance;
}

export type TagImportance = -1 | 0 | 1;

/** A prefilled draft read from a pasted link. Nothing is saved until the entry is saved. */
export interface CapturedLink {
  source_url: string;
  title: string;
  description: string;
  kind: string;
  source_name: string;
  occurred_at: string | null;
  media: MediaItem[];
}
