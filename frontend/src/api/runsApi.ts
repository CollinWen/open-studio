/**
 * Calls to the backend's run endpoints (backend/app/features/runs/routes.py),
 * for the owner: every run, newest first, and issuing a token, which starts
 * a run and returns its kit once. Agents finish their own runs.
 */

import type { Run, RunCreate, RunKit } from "../types/run";
import { backendRequest } from "./backendRequest";

export const fetchRuns = () => backendRequest<Run[]>("/api/runs");

export const issueToken = (run: RunCreate) =>
  backendRequest<RunKit>("/api/runs", { method: "POST", body: JSON.stringify(run) });
