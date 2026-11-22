/**
 * describeRunState: a run's state in a few plain words, with how long ago:
 * "running, started 2 h ago", "finished 5 min ago", "ran out 3 days ago".
 *
 * Used by RunList.
 */

import type { Run } from "../../types/run";
import { formatTimeAgo } from "../agents/formatTimeAgo";

export function describeRunState(run: Run, now = Date.now()): string {
  if (run.state === "finished" && run.finished_at) return `finished ${formatTimeAgo(run.finished_at, now)}`;
  if (run.state === "expired") return `ran out ${formatTimeAgo(run.expires_at, now)}`;
  return `running, started ${formatTimeAgo(run.created_at, now)}`;
}
