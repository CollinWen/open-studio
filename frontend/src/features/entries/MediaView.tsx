/**
 * MediaView: one picture, video or write-up at full size on an entry page.
 * Images show the original file; embeds (YouTube, Drive video) show the
 * site's own player at 16:9; a write-up is read in the studio's own style
 * (WriteupView). Pictures fade in as they load. A caption, if any, sits underneath.
 */

import { FadeInImage } from "../../components/FadeInImage";
import type { MediaItem } from "../../types/entry";
import { WriteupView } from "./WriteupView";

export function MediaView({ item, title }: { item: MediaItem; title: string }) {
  if (item.type === "html") return <WriteupView item={item} title={title} />;
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
      {item.caption && <figcaption className="quiet">{item.caption}</figcaption>}
    </figure>
  );
}
