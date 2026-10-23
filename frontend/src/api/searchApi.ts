/**
 * Asks the backend for entries matching a typed query, best match first
 * (by meaning when embeddings exist, plus plain word matches), on one board or all.
 */

import type { Entry } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const searchEntries = (query: string, board?: string) =>
  backendRequest<Entry[]>(
    `/api/search?q=${encodeURIComponent(query)}${board ? `&board=${encodeURIComponent(board)}` : ""}`,
  );
