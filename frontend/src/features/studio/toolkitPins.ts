/**
 * toolkitPins: a toolkit grant's pinned arguments as one line of text and
 * back, for the agent window: "owner=CollinWen; repo=open-studio, proto-*"
 * (each argument, then its allowed values; "proto-*" allows any value that
 * starts with "proto-"). An argument with no values is dropped.
 *
 * Used by ToolkitGrantForm and ToolkitGrantsEditor.
 */

export function formatPins(pins: Record<string, string[]>): string {
  return Object.entries(pins)
    .map(([name, values]) => `${name}=${values.join(", ")}`)
    .join("; ");
}

export function parsePins(text: string): Record<string, string[]> {
  const pins: Record<string, string[]> = {};
  for (const part of text.split(";")) {
    const equals = part.indexOf("=");
    if (equals < 0) continue;
    const name = part.slice(0, equals).trim();
    const values = part
      .slice(equals + 1)
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    if (name && values.length) pins[name] = values;
  }
  return pins;
}
