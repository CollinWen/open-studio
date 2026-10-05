/**
 * Calls to the backend's entry endpoints (backend/app/features/entries/routes.py),
 * plus "Related" entries.
 */

import type { Entry, EntryDraft } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchEntries = () => backendRequest<Entry[]>("/api/entries");

export const fetchEntry = (id: string) => backendRequest<Entry>(`/api/entries/${id}`);

export const fetchRelatedEntries = (id: string) => backendRequest<Entry[]>(`/api/entries/${id}/related`);

export const createEntry = (draft: EntryDraft) =>
  backendRequest<Entry>("/api/entries", { method: "POST", body: JSON.stringify(draft) });

export const updateEntry = (id: string, draft: Partial<EntryDraft>) =>
  backendRequest<Entry>(`/api/entries/${id}`, { method: "PATCH", body: JSON.stringify(draft) });

export const deleteEntry = (id: string) => backendRequest<void>(`/api/entries/${id}`, { method: "DELETE" });
