/**
 * Agent data shapes, matching backend/app/features/agents/schemas.py and
 * backend/app/features/agent_log/schemas.py.
 */

export interface Agent {
  name: string;
  description: string;
  /** A paused agent can read, but not add or log anything. */
  active: boolean;
  /** One line the agent sets on itself: what it's doing now. */
  status: string;
  last_seen_at: string | null;
  created_at: string;
  /** Boards it's signed on to. */
  boards: string[];
}

/** Returned when an agent is added or re-keyed: the only time its token is shown. */
export interface AgentWithToken {
  agent: Agent;
  token: string;
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
