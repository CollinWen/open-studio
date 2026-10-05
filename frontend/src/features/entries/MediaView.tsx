/**
 * MediaView: one picture or video at full size on an entry page.
 * Images show the original file; embeds (YouTube, Drive video) show the
 * site's own player at 16:9. A caption, if any, sits underneath.
 */

import type { MediaItem } from "../../types/entry";

export function MediaView({ item, title }: { item: MediaItem; title: string }) {
  return (
    <figure className="media-view">
      {item.type === "image" && <img src={item.url} alt={item.caption || title} loading="lazy" />}
      {item.type === "video" && <video src={item.url} controls playsInline />}
      {item.type === "embed" && (
        <iframe
          src={item.url}
          title={item.caption || title}
          allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
          allowFullScreen
        />
      )}
      {item.caption && <figcaption className="quiet">{item.caption}</figcaption>}
    </figure>
  );
}
