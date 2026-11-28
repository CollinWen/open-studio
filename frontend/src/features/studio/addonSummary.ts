/**
 * addonSummary: one plain line saying what an add-on is, read from the
 * start of its guide ("**What it is:** a shell in your own sandbox…" →
 * "a shell in your own sandbox…"), for the add-ons list and the hint on an
 * add-on's oval in the agent window.
 *
 * Used by AddonManager and AddonPicker.
 */

export function summarizeAddon(guide: string): string {
  const first = guide.split("\n").find((line) => line.trim()) ?? "";
  return first
    .trim()
    .replace(/^#+\s*/, "")
    .replace(/^\*\*[^*]+:\*\*\s*/, "")
    .replace(/[*_`]/g, "");
}
