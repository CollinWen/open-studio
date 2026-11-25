/**
 * Calls to the backend's toolkit endpoints (backend/app/features/toolkits/routes.py)
 * for the owner: every tool of one toolkit on Composio, optionally narrowed
 * by words, to pick an agent's tools from. Grants are saved with the agent
 * (agentsApi.ts); agents call their tools through the studio themselves.
 */

import type { CatalogTool } from "../types/toolkit";
import { backendRequest } from "./backendRequest";

export const fetchToolkitCatalog = (toolkit: string, words = "") =>
  backendRequest<CatalogTool[]>(
    `/api/toolkits/${encodeURIComponent(toolkit)}/catalog${words ? `?q=${encodeURIComponent(words)}` : ""}`,
  );
