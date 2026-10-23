/**
 * Calls to the backend's tag endpoints: which tags exist, and (owner only)
 * saving a tag's description and importance. Pass a board slug to count one board's entries only.
 */

import type { Tag, TagImportance } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchTags = (board?: string) =>
  backendRequest<Tag[]>(board ? `/api/tags?board=${encodeURIComponent(board)}` : "/api/tags");

export const saveTagNotes = (name: string, notes: { description: string; importance: TagImportance }) =>
  backendRequest<void>(`/api/tags/${encodeURIComponent(name)}`, { method: "PUT", body: JSON.stringify(notes) });
