/**
 * MediaListEditor: the pictures and videos in the entry being edited.
 * Each one shows as a small preview with "cover" (move to first), "remove"
 * and a caption. "add file" uploads from this device, stored untouched.
 */

import { useState } from "react";
import { uploadMedia } from "../../api/mediaApi";
import type { MediaItem } from "../../types/entry";

interface Props {
  media: MediaItem[];
  onChange: (media: MediaItem[]) => void;
}

export function MediaListEditor({ media, onChange }: Props) {
  const [status, setStatus] = useState("");

  async function addFiles(files: FileList | null) {
    if (!files?.length) return;
    setStatus("uploading…");
    try {
      const added: MediaItem[] = [];
      for (const file of Array.from(files)) {
        const url = await uploadMedia(file);
        const type = file.type.startsWith("video/") ? "video" : "image";
        added.push({ type, url, thumbnail_url: "", caption: "" });
      }
      onChange([...media, ...added]);
      setStatus("");
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
          <img src={item.thumbnail_url || item.url} alt="" />
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
        <input type="file" accept="image/*,video/*" multiple hidden onChange={(e) => addFiles(e.target.files)} />
      </label>
      {status && <span className="quiet"> {status}</span>}
    </div>
  );
}
