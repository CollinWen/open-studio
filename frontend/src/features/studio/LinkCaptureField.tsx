/**
 * LinkCaptureField: paste a link (YouTube, Google Drive, GitHub, any page),
 * press enter, and the backend reads it. The result is handed to the form,
 * which fills in empty fields and adds the link's pictures.
 *
 * Paste several Drive photo links one after another to build a series.
 */

import { useState } from "react";
import { captureLink } from "../../api/captureApi";
import { LoadingWord } from "../../components/LoadingWord";
import type { CapturedLink } from "../../types/entry";

interface Props {
  onCaptured: (captured: CapturedLink) => void;
  /** Put the cursor here straight away (a new entry usually starts from a link). */
  autoFocus?: boolean;
}

const READING = "reading…";

export function LinkCaptureField({ onCaptured, autoFocus = false }: Props) {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");

  async function read() {
    if (!url.trim()) return;
    setStatus(READING);
    try {
      onCaptured(await captureLink(url.trim()));
      setUrl("");
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  return (
    <div>
      <input
        autoFocus={autoFocus}
        placeholder="paste a link, then enter (youtube, google drive, github, any page)"
        value={url}
        onChange={(event) => setUrl(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            read();
          }
        }}
      />
      {status === READING && (
        <p>
          <LoadingWord>{status}</LoadingWord>
        </p>
      )}
      {status && status !== READING && <p className="quiet">{status}</p>}
    </div>
  );
}
