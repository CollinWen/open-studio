/**
 * Calls to the backend's agent log (backend/app/features/agent_log/routes.py):
 * what agents are planning, thinking, finding and asking, newest first,
 * narrowed by agent, board, type of line or words in the text. Pass the
 * oldest line's time as `before` for the next page.
 */

import type { LogLine } from "../types/agent";
import { backendRequest } from "./backendRequest";

export interface LogFilters {
  agent?: string;
  board?: string;
  type?: string;
  q?: string;
  before?: string;
}

export function fetchAgentLog(filters: LogFilters) {
  const params = new URLSearchParams();
  for (const [name, value] of Object.entries(filters)) if (value) params.set(name, value);
  const query = params.toString();
  return backendRequest<LogLine[]>(query ? `/api/agent-log?${query}` : "/api/agent-log");
}
