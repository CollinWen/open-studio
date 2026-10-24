/**
 * Calls to the backend's agent log (backend/app/features/agent_log/routes.py):
 * what agents are planning, thinking, finding and asking, newest first,
 * for one agent, one board, or everyone. Pass the oldest line's time as
 * `before` for the next page.
 */

import type { LogLine } from "../types/agent";
import { backendRequest } from "./backendRequest";

export function fetchAgentLog(filters: { agent?: string; board?: string; before?: string }) {
  const params = new URLSearchParams();
  for (const [name, value] of Object.entries(filters)) if (value) params.set(name, value);
  const query = params.toString();
  return backendRequest<LogLine[]>(query ? `/api/agent-log?${query}` : "/api/agent-log");
}
