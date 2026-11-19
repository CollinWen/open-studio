/**
 * webAddress: turns what was typed or pasted into the entry form's link field
 * into a web address: without surrounding spaces, and with https:// added to a
 * bare one like "example.com/recipe" or "www.youtube.com/watch?v=…", which is
 * how links often arrive from an address bar or a chat. Anything else (a word,
 * another scheme) is left as it is, so the backend can say why it's refused.
 *
 * Used by LinkCaptureField. The rule for what an address may be lives in the
 * backend (entries/schemas.py).
 */

// A scheme at the start ("https:", "mailto:", "javascript:"): left alone.
const HAS_SCHEME = /^[a-z][a-z0-9+.-]*:/i;
// A bare address: a domain with a dot (no spaces anywhere), then maybe a path.
const BARE_ADDRESS = /^[a-z0-9-]+(\.[a-z0-9-]+)+(:\d+)?([/?#]\S*)?$/i;

export function toWebAddress(text: string): string {
  const trimmed = text.trim();
  if (!trimmed || HAS_SCHEME.test(trimmed) || !BARE_ADDRESS.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}
