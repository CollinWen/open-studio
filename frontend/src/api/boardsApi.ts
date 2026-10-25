/**
 * Calls to the backend's board endpoints (backend/app/features/boards/routes.py):
 * which boards exist (each a separate space with its own entries), and, for
 * the owner, making a board and changing its name, brief or agents.
 */

import type { Board } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchBoards = () => backendRequest<Board[]>("/api/boards");

/** Owner only. slug: lowercase letters, digits and dashes; the board lives at /b/<slug>. */
export const createBoard = (board: { slug: string; name: string; description: string }) =>
  backendRequest<Board>("/api/boards", { method: "POST", body: JSON.stringify(board) });

/** Owner only: change a board's name or brief. */
export const updateBoard = (slug: string, changes: { name?: string; description?: string }) =>
  backendRequest<Board>(`/api/boards/${encodeURIComponent(slug)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });

/** Owner only: which agents may add to a board. */
export const setBoardAgents = (slug: string, agents: string[]) =>
  backendRequest<Board>(`/api/boards/${encodeURIComponent(slug)}`, {
    method: "PATCH",
    body: JSON.stringify({ agents }),
  });
