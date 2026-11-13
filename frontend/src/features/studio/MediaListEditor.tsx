/**
 * MediaListEditor: the pictures, videos and write-ups in the entry being edited.
 * Each one shows as a small preview with "cover" (move to first), "remove"
 * and a caption. "add file" uploads from this device: pictures and videos
 * are stored untouched; a write-up (.html) is made safe first, and what was
 * removed from it is listed here.
 */

import { useState } from "react";
import { uploadMedia } from "../../api/mediaApi";
import { LoadingWord } from "../../components/LoadingWord";
import type { MediaItem } from "../../types/entry";

interface Props {
  media: MediaItem[];
  onChange: (media: MediaItem[]) => void;
}

const UPLOADING = "uploading…";

export function MediaListEditor({ media, onChange }: Props) {
  const [status, setStatus] = useState("");

  async function addFiles(files: FileList | null) {
    if (!files?.length) return;
    setStatus(UPLOADING);
    try {
      const added: MediaItem[] = [];
      const removed: string[] = [];
      for (const file of Array.from(files)) {
        const uploaded = await uploadMedia(file);
        added.push({ type: mediaTypeOf(file), url: uploaded.url, thumbnail_url: "", caption: "" });
        removed.push(...(uploaded.removed ?? []));
      }
      onChange([...media, ...added]);
      setStatus(removed.length ? `removed from the write-up: ${removed.join(", ")}` : "");
    } catch (error) {
      setStatus(`upload failed: ${error instanceof Error ? error.message : error}`);
    }
  }

  const makeCover = (index: number) => onChange([media[index], ...media.filter((_, i) => i !== index)]);
  const remove = (index: number) => onChange(media.filter((_, i) => i !== index));
  const setCaption = (index: number, caption: string) =>
    onChange(media.map((item, i) => (i === index ? { ...item, caption } : item)));

  return (
    <div className="media-editor">
      {media.map((item, index) => (
        <div key={`${item.url}-${index}`} className="media-editor-item">
          {item.type === "html" ? (
            <span className="media-editor-writeup quiet">write-up</span>
          ) : (
            <img src={item.thumbnail_url || item.url} alt="" />
          )}
          <div className="word-list">
            <span className="quiet">{index === 0 ? "cover" : item.type}</span>
            <input placeholder="caption" value={item.caption} onChange={(e) => setCaption(index, e.target.value)} />
            {index > 0 && (
              <button type="button" className="quiet" onClick={() => makeCover(index)}>
                make cover
              </button>
            )}
            <button type="button" className="quiet" onClick={() => remove(index)}>
              remove
            </button>
          </div>
        </div>
      ))}
      <label className="quiet">
        add file
        <input type="file" accept="image/*,video/*,.html" multiple hidden onChange={(e) => addFiles(e.target.files)} />
      </label>
      {status === UPLOADING && <LoadingWord> {status}</LoadingWord>}
      {status && status !== UPLOADING && <span className="quiet"> {status}</span>}
    </div>
  );
}

function mediaTypeOf(file: File): MediaItem["type"] {
  if (file.name.toLowerCase().endsWith(".html")) return "html";
  return file.type.startsWith("video/") ? "video" : "image";
}
