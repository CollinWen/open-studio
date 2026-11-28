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
  /** Skills it works with, by name (folders in the agent resources). */
  skills: string[];
  /** The add-ons it uses, by name (types/addon.ts). */
  addons: string[];
  /** The owner's instructions for any of its add-ons, by add-on. Only the owner sees them; others get {}. */
  addon_instructions: Record<string, string>;
}

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
