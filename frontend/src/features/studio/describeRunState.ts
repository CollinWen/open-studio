/**
 * describeRunState: a run's state in a few plain words, with how long ago:
 * "running, started 2 h ago, until Dec 24, 9:30 PM", "finished 5 min ago",
 * "ran out 3 days ago".
 *
 * Used by RunList.
 */

import type { Run } from "../../types/run";
import { formatTimeAgo, parseServerTime } from "../agents/formatTimeAgo";

export function describeRunState(run: Run, now = Date.now()): string {
  if (run.state === "finished" && run.finished_at) return `finished ${formatTimeAgo(run.finished_at, now)}`;
  if (run.state === "expired") return `ran out ${formatTimeAgo(run.expires_at, now)}`;
  const until = parseServerTime(run.expires_at).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
  return `running, started ${formatTimeAgo(run.created_at, now)}, until ${until}`;
}
