/**
 * MediaListEditor: the pictures and videos in the entry being edited.
 * Each one shows as a small preview with "cover" (move to first), "remove"
 * and a caption. "add file" uploads from this device, stored untouched; each
 * upload keeps its size (shown here and on the entry page), and the uploading
 * line shows the total.
 */

import { useState } from "react";
import { uploadMedia } from "../../api/mediaApi";
import { LoadingWord } from "../../components/LoadingWord";
import type { MediaItem } from "../../types/entry";
import { formatFileSize } from "../entries/formatFileSize";

interface Props {
  media: MediaItem[];
  onChange: (media: MediaItem[]) => void;
}

export function MediaListEditor({ media, onChange }: Props) {
  const [status, setStatus] = useState("");
  const [uploading, setUploading] = useState(false);

  async function addFiles(files: FileList | null) {
    if (!files?.length) return;
    const picked = Array.from(files);
    const total = picked.reduce((sum, file) => sum + file.size, 0);
    setUploading(true);
    setStatus(`uploading ${picked.length === 1 ? "1 file" : `${picked.length} files`} · ${formatFileSize(total)}…`);
    try {
      const added: MediaItem[] = [];
      for (const file of picked) {
        const url = await uploadMedia(file);
        const type = file.type.startsWith("video/") ? "video" : "image";
        added.push({ type, url, thumbnail_url: "", caption: "", size_bytes: file.size });
      }
      onChange([...media, ...added]);
      setStatus("");
    } catch (error) {
      setStatus(`upload failed: ${error instanceof Error ? error.message : error}`);
    } finally {
      setUploading(false);
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
            {item.size_bytes > 0 && <span className="quiet">{formatFileSize(item.size_bytes)}</span>}
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
      {uploading && <LoadingWord> {status}</LoadingWord>}
      {status && !uploading && <span className="quiet"> {status}</span>}
    </div>
  );
}
