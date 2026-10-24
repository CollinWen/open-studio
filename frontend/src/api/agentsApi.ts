/**
 * Calls to the backend's agent endpoints (backend/app/features/agents/routes.py):
 * every agent and what it's doing (anyone), and, for the owner, adding,
 * pausing, re-keying and removing agents. Which boards an agent is on is
 * changed on the board (see boardsApi.ts).
 */

import type { Agent, AgentWithToken } from "../types/agent";
import { backendRequest } from "./backendRequest";

export const fetchAgents = () => backendRequest<Agent[]>("/api/agents");

export const addAgent = (agent: { name: string; description: string; boards: string[] }) =>
  backendRequest<AgentWithToken>("/api/agents", { method: "POST", body: JSON.stringify(agent) });

export const updateAgent = (name: string, changes: { description?: string; active?: boolean }) =>
  backendRequest<Agent>(`/api/agents/${encodeURIComponent(name)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });

export const renewAgentToken = (name: string) =>
  backendRequest<AgentWithToken>(`/api/agents/${encodeURIComponent(name)}/token`, { method: "POST" });

export const removeAgent = (name: string) =>
  backendRequest<void>(`/api/agents/${encodeURIComponent(name)}`, { method: "DELETE" });
