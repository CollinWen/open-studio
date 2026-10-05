/**
 * Formats an entry's date the same way everywhere: "October 3, 2026".
 */

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}
