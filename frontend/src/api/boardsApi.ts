/**
 * Calls to the backend's board endpoints (backend/app/features/boards/routes.py):
 * which boards exist (each a separate space with its own entries), and, for
 * the owner, which agents may add to one.
 */

import type { Board } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchBoards = () => backendRequest<Board[]>("/api/boards");

/** Owner only: which agents may add to a board. */
export const setBoardAgents = (slug: string, agents: string[]) =>
  backendRequest<Board>(`/api/boards/${encodeURIComponent(slug)}`, {
    method: "PATCH",
    body: JSON.stringify({ agents }),
  });
