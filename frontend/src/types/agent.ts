/**
 * Agent data shapes, matching backend/app/features/agents/schemas.py and
 * backend/app/features/agent_log/schemas.py.
 */

export interface Agent {
  name: string;
  /** One line on what it's for, for the agent lists. */
  description: string;
  /** Its standing job, written into every run's prompt: objective, focus, which tools for what, what it hands back. */
  manifest: string;
  /** A paused agent can read, but not add or log anything. */
  active: boolean;
  /** One line the agent sets on itself: what it's doing now. */
  status: string;
  last_seen_at: string | null;
  created_at: string;
  /** Boards it's signed on to. */
  boards: string[];
  /** Outside tools its runs may be given (backend/app/features/runs/outside_tools.py). */
  tools: OutsideTool[];
  /** Skills it works with, picked from AGENT_SKILLS. */
  skills: AgentSkill[];
}

/**
 * The skills the owner can pick for an agent, one folder each in skills/
 * (backend/app/features/agents/schemas.py keeps the same list). Every agent
 * also loads open-studio and studio-collaborator, so they aren't here.
 */
export const AGENT_SKILLS = [
  "gathering-sources",
  "studying-sources",
  "brainstorming",
  "building",
  "studio-writeup",
  "linking-entries",
] as const;
export type AgentSkill = (typeof AGENT_SKILLS)[number];

/** What a run may use beyond the studio: search and read the web, run code, make a GitHub repository. */
export const OUTSIDE_TOOLS = ["web", "code", "github"] as const;
export type OutsideTool = (typeof OUTSIDE_TOOLS)[number];

export type LogLineType = "plan" | "thought" | "finding" | "question" | "status";

/** One line an agent wrote in the agent log. */
export interface LogLine {
  id: string;
  agent: string;
  board: string | null;
  type: LogLineType;
  text: string;
  entry_id: string | null;
  /** Set when you may see the entry, so the line can link to it by name. */
  entry_title: string | null;
  created_at: string;
}
