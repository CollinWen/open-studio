/**
 * Calls to the backend's agent endpoints (backend/app/features/agents/routes.py):
 * every agent and what it's doing (anyone), and, for the owner, adding,
 * changing (description, boards, outside tools, skills), pausing and removing
 * agents, and every agent as agents.yaml. Agents have no token of their own:
 * tokens are runs (runsApi.ts).
 */

import type { Agent, OutsideTool } from "../types/agent";
import { backendRequest } from "./backendRequest";

export const fetchAgents = () => backendRequest<Agent[]>("/api/agents");

export interface AgentSettings {
  description: string;
  boards: string[];
  tools: OutsideTool[];
  skills: string[];
}

export const addAgent = (agent: { name: string } & AgentSettings) =>
  backendRequest<Agent>("/api/agents", { method: "POST", body: JSON.stringify(agent) });

export const updateAgent = (name: string, changes: Partial<AgentSettings> & { active?: boolean }) =>
  backendRequest<Agent>(`/api/agents/${encodeURIComponent(name)}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });

export const removeAgent = (name: string) =>
  backendRequest<void>(`/api/agents/${encodeURIComponent(name)}`, { method: "DELETE" });

/** Every agent as agents.yaml (no tokens), as text, for the owner to download. */
export const fetchAgentsYaml = () => backendRequest<string>("/api/agents/export", { asText: true });
