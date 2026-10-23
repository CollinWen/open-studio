/**
 * Calls to the backend's board endpoints (backend/app/features/boards/routes.py):
 * which boards exist. Each board is a separate space with its own entries.
 */

import type { Board } from "../types/entry";
import { backendRequest } from "./backendRequest";

export const fetchBoards = () => backendRequest<Board[]>("/api/boards");
