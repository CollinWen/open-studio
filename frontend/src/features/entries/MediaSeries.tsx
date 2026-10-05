/**
 * MediaSeries: every picture and video in an entry, one after another in a
 * single column, cover first. No carousel or arrows: you just scroll.
 */

import type { MediaItem } from "../../types/entry";
import { MediaView } from "./MediaView";

export function MediaSeries({ media, title }: { media: MediaItem[]; title: string }) {
  if (media.length === 0) return null;
  return (
    <div className="media-series">
      {media.map((item, index) => (
        <MediaView key={`${item.url}-${index}`} item={item} title={title} />
      ))}
    </div>
  );
}
