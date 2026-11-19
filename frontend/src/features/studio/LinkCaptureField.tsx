/**
 * LinkCaptureField: the entry form's one link field, which is the entry's
 * source url, so whatever is in it is saved with the entry. Pasting a link
 * (YouTube, Google Drive, GitHub, any page), or pressing enter, also asks
 * the backend to read it; the result goes to the form, which fills in the
 * fields that are still empty and adds the link's pictures.
 *
 * Paste several Drive photo links one after another to build a series:
 * each one's pictures are added, and the last link stays as the source.
 *
 * What's typed or pasted is made a web address first (webAddress.ts): spaces
 * trimmed, and https:// added to a bare "example.com/recipe".
 */

import { useState } from "react";
import { captureLink } from "../../api/captureApi";
import { LoadingWord } from "../../components/LoadingWord";
import type { CapturedLink } from "../../types/entry";
import { toWebAddress } from "./webAddress";

interface Props {
  url: string;
  onChange: (url: string) => void;
  onCaptured: (captured: CapturedLink) => void;
}

const READING = "reading the link…";

export function LinkCaptureField({ url, onChange, onCaptured }: Props) {
  const [status, setStatus] = useState("");

  async function read(typed: string) {
    const link = toWebAddress(typed);
    if (!link) return;
    onChange(link);
    setStatus(READING);
    try {
      onCaptured(await captureLink(link));
      setStatus("");
    } catch (error) {
      setStatus(`couldn't read it (${error instanceof Error ? error.message : error}); the link is still kept`);
    }
  }

  return (
    <div>
      <input
        inputMode="url"
        placeholder="link (paste one to fill in the rest)"
        value={url}
        onChange={(event) => onChange(event.target.value)}
        onBlur={() => onChange(toWebAddress(url))}
        onPaste={(event) => {
          // The pasted link replaces the field, already made a web address.
          event.preventDefault();
          read(event.clipboardData.getData("text"));
        }}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            read(url);
          }
        }}
      />
      {status === READING && <LoadingWord>{status}</LoadingWord>}
      {status && status !== READING && <p className="quiet">{status}</p>}
    </div>
  );
}
