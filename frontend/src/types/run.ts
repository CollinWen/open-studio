/**
 * Run data shapes, matching backend/app/features/runs/schemas.py (RunOut):
 * one task given to one agent, its state, and where to watch it work.
 */

import type { OutsideTool } from "./agent";

export type RunState = "running" | "finished" | "expired";

export interface Run {
  id: string;
  agent: string;
  /** study, references or prototype (backend/app/features/runs/task_kinds.py). */
  kind: string;
  board: string;
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
