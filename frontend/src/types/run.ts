/**
 * Run data shapes, matching backend/app/features/runs/schemas.py: a run is
 * one session of one agent, which is one token (open, or with a task); what
 * the owner sends to issue one; and the kit that comes back once, with the token.
 */

import type { OutsideTool } from "./agent";

export type RunState = "running" | "finished" | "expired";

/** What a run is: no set task (open), or one of the task kinds. */
export const RUN_KINDS = ["open", "study", "references", "prototype"] as const;
export type RunKind = (typeof RUN_KINDS)[number];

/** In a run's boards: every board its agent is signed on to, now or later. */
export const ALL_BOARDS = "*";

export interface Run {
  id: string;
  agent: string;
  /** open, study, references or prototype (backend/app/features/runs/task_kinds.py). */
  kind: RunKind;
  /** Slugs, or ["*"]: every board its agent is signed on to. */
  boards: string[];
  /** The owner's note: what to do, in their words. */
  brief: string;
  entry_id: string | null;
  tools: OutsideTool[];
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
  kind: RunKind;
  boards: string[];
  brief: string;
  /** Leave out for the kind's usual tools (an open run: all its agent was granted). */
  tools?: OutsideTool[];
  minutes: number;
}

/** A ready way to run the kit in one particular harness. */
export interface HarnessSetup {
  command: string;
  allowed_tools: string[];
}

/** Returned once, when a token is issued: the token is never shown again. */
export interface RunKit {
  run: Run;
  token: string;
  mcp_url: string;
  api_url: string;
  prompt: string;
  /** By harness name ("claude_code"): optional ready-made commands. */
  setups: Record<string, HarnessSetup>;
}
