/**
 * LinkCaptureField: paste a link (YouTube, Google Drive, GitHub, any page),
 * press enter, and the backend reads it. The result is handed to the form,
 * which fills in empty fields and adds the link's pictures.
 *
 * Paste several Drive photo links one after another to build a series.
 */

import { useState } from "react";
import { captureLink } from "../../api/captureApi";
import type { CapturedLink } from "../../types/entry";

export function LinkCaptureField({ onCaptured }: { onCaptured: (captured: CapturedLink) => void }) {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");

  async function read() {
    if (!url.trim()) return;
    setStatus("reading…");
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
      {status && <p className="quiet">{status}</p>}
    </div>
  );
}
