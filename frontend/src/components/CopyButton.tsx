/**
 * CopyButton: a word that copies some text to the clipboard and says
 * "copied" for a moment after.
 *
 * Used by TokenNotice (a token and its setups) and AgentsMdView.
 */

import { useState } from "react";

const COPIED_FOR_MS = 1500;

export function CopyButton({ text, label = "copy" }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () =>
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), COPIED_FOR_MS);
    });
  return (
    <button type="button" className="square quiet" onClick={copy}>
      {copied ? "copied" : label}
    </button>
  );
}
