/**
 * Calls to the backend's entry endpoints (backend/app/features/entries/routes.py),
 * plus "Related" entries. Pass a board slug to keep one board; leave it out for every board.
 */

import type { Entry, EntryDraft, EntryPage } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchEntries = (board?: string) =>
  backendRequest<Entry[]>(board ? `/api/entries?board=${encodeURIComponent(board)}` : "/api/entries");

/** One page of a board's entries, newest first. Pass the previous page's next_cursor for the page after. */
export const fetchEntryPage = (board: string, limit: number, cursor: string | null) => {
  const params = new URLSearchParams({ board, limit: String(limit) });
  if (cursor) params.set("cursor", cursor);
  return backendRequest<EntryPage>(`/api/entries/page?${params}`);
};

export const fetchEntry = (id: string) => backendRequest<Entry>(`/api/entries/${id}`);

export const fetchRelatedEntries = (id: string) => backendRequest<Entry[]>(`/api/entries/${id}/related`);

export const createEntry = (draft: EntryDraft) =>
  backendRequest<Entry>("/api/entries", { method: "POST", body: JSON.stringify(draft) });

export const updateEntry = (id: string, draft: Partial<EntryDraft>) =>
  backendRequest<Entry>(`/api/entries/${id}`, { method: "PATCH", body: JSON.stringify(draft) });

export const deleteEntry = (id: string) => backendRequest<void>(`/api/entries/${id}`, { method: "DELETE" });
