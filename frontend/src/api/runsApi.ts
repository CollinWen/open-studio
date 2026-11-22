/**
 * Calls to the backend's run endpoints (backend/app/features/runs/routes.py):
 * every run, newest first, for the owner. Runs are started and finished by
 * agents and their harnesses, not from the site.
 */

import type { Run } from "../types/run";
import { backendRequest } from "./backendRequest";

export const fetchRuns = () => backendRequest<Run[]>("/api/runs");
