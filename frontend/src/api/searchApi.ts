/**
 * Asks the backend for entries matching a typed query, best match first
 * (by meaning when embeddings exist, plus plain word matches).
 */

import type { Entry } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const searchEntries = (query: string) =>
  backendRequest<Entry[]>(`/api/search?q=${encodeURIComponent(query)}`);
