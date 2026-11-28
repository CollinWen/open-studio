/**
 * Calls to the backend's agent endpoints (backend/app/features/agents/routes.py):
 * every agent and what it's doing (anyone), and, for the owner, adding,
 * changing (description, manifest, boards, skills, add-ons and the
 * instructions for each), pausing and removing agents, one agent's AGENTS.md
 * as its runs get it, and every agent as agents.yaml. Agents have no token of
 * their own: tokens are runs (runsApi.ts).
 */

import type { Agent } from "../types/agent";
import { backendRequest } from "./backendRequest";

export const fetchAgents = () => backendRequest<Agent[]>("/api/agents");

export interface AgentSettings {
  description: string;
  manifest: string;
  boards: string[];
  skills: string[];
  addons: string[];
  addon_instructions: Record<string, string>;
}

const agentPath = (name: string) => `/api/agents/${encodeURIComponent(name)}`;

export const addAgent = (agent: { name: string } & AgentSettings) =>
  backendRequest<Agent>("/api/agents", { method: "POST", body: JSON.stringify(agent) });

export const updateAgent = (name: string, changes: Partial<AgentSettings> & { active?: boolean }) =>
  backendRequest<Agent>(agentPath(name), { method: "PATCH", body: JSON.stringify(changes) });

export const removeAgent = (name: string) => backendRequest<void>(agentPath(name), { method: "DELETE" });

/** The AGENTS.md its runs get, from its settings as saved: what it has and how to use each. */
export const fetchAgentsMd = (name: string) => backendRequest<string>(`${agentPath(name)}/agents-md`, { asText: true });

/** Every agent as agents.yaml (no tokens), as text, for the owner to download. */
export const fetchAgentsYaml = () => backendRequest<string>("/api/agents/export", { asText: true });
