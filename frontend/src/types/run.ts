/**
 * Run data shapes, matching backend/app/features/runs/schemas.py: a run is
 * one session of one agent, which is one token: what it may reach and for how
 * long; what the owner sends to issue one; and the kit that comes back once,
 * with the token. What the agent is for is its manifest (types/agent.ts).
 */

export type RunState = "running" | "finished" | "expired";

/** In a run's boards: every board its agent is signed on to, now or later. */
export const ALL_BOARDS = "*";

export interface Run {
  id: string;
  agent: string;
  /** Slugs, or ["*"]: every board its agent is signed on to. */
  boards: string[];
  /** The add-ons it may use, by name: its agent's, or fewer. */
  addons: string[];
  /** "owner" or "agent:<name>". */
  started_by: string;
  created_at: string;
  expires_at: string;
  finished_at: string | null;
  /** The harness's own page for this run (e.g. a claude.ai/code session); "" until the agent sets it. */
  session_url: string;
  /** What the agent says it did, left when it finished. */
  summary: string;
  state: RunState;
  scopes: string[];
  /** Ids of the entries it added. */
  added: string[];
}

/** What the owner sends to issue a token. */
export interface RunCreate {
  agent: string;
  boards: string[];
  /** Leave out for all its agent's add-ons. */
  addons?: string[];
  minutes: number;
}

/** A ready way to run the kit in one particular harness. */
export interface HarnessSetup {
  /** One line to paste in an empty folder where that harness is installed: it sets up the run's sandbox there and starts it. */
  command: string;
  /** That harness's names for the tools the run may use. */
  allowed_tools: string[];
}

/** Returned once, when a token is issued: the token is never shown again. */
export interface RunKit {
  run: Run;
  token: string;
  mcp_url: string;
  api_url: string;
  prompt: string;
  /** The script that sets up a sandbox for whichever run's token fetches it (?harness=claude_code for Claude Code). */
  sandbox_url: string;
  /** By harness name ("pi", "claude_code"): one line that sets up a sandbox and runs the task. */
  setups: Record<string, HarnessSetup>;
}
