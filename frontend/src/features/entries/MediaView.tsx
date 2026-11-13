/**
 * MediaView: one picture or video at full size on an entry page.
 * Images show the original file; embeds (YouTube, Drive video) show the
 * site's own player at 16:9. Pictures fade in as they load. Underneath, in
 * one quiet line: the caption, if any, and an upload's file size, if known.
 */

import { FadeInImage } from "../../components/FadeInImage";
import type { MediaItem } from "../../types/entry";
import { formatFileSize } from "./formatFileSize";

export function MediaView({ item, title }: { item: MediaItem; title: string }) {
  return (
    <figure className="media-view">
      {item.type === "image" && <FadeInImage src={item.url} alt={item.caption || title} loading="lazy" />}
      {item.type === "video" && <video src={item.url} controls playsInline />}
      {item.type === "embed" && (
        <iframe
          src={item.url}
          title={item.caption || title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
        />
      )}
      {(item.caption || item.size_bytes > 0) && (
        <figcaption className="quiet word-list">
          {item.caption && <span>{item.caption}</span>}
          {item.size_bytes > 0 && <span>{formatFileSize(item.size_bytes)}</span>}
        </figcaption>
      )}
    </figure>
  );
}
