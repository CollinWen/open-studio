/**
 * formatTimeAgo: how long ago something happened, in a few plain words
 * ("just now", "12 min ago", "3 h ago", "2 days ago"), then the date once
 * it's more than a week old. For the agents page, where "when" matters
 * more as "how recently" than as a date.
 *
 * The backend sends times without a zone; they're always UTC.
 */

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export function formatTimeAgo(iso: string, now = Date.now()): string {
  const then = parseServerTime(iso);
  const ago = now - then.getTime();
  if (ago < MINUTE) return "just now";
  if (ago < HOUR) return `${Math.floor(ago / MINUTE)} min ago`;
  if (ago < DAY) return `${Math.floor(ago / HOUR)} h ago`;
  if (ago < 7 * DAY) return `${Math.floor(ago / DAY)} ${ago < 2 * DAY ? "day" : "days"} ago`;
  return then.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function parseServerTime(iso: string): Date {
  return new Date(/Z|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`);
}
