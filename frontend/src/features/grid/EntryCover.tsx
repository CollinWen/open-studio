/**
 * EntryCover: the picture shown for an entry in the grid. The first media
 * item, using its smaller thumbnail when it has one (so the grid loads fast
 * and embeds like YouTube show a still instead of a player).
 * Videos play silently on loop, like a moving picture; pictures fade in as
 * they load.
 */

import { FadeInImage } from "../../components/FadeInImage";
import type { MediaItem } from "../../types/entry";

export function EntryCover({ media, title }: { media: MediaItem[]; title: string }) {
  const cover = media[0];
  if (!cover) return null;

  const extra = media.length > 1 ? ` (+${media.length - 1})` : "";
  if (cover.type === "video" && !cover.thumbnail_url) {
    return <video className="entry-cover" src={cover.url} muted autoPlay loop playsInline aria-label={title + extra} />;
  }
  return <FadeInImage className="entry-cover" src={cover.thumbnail_url || cover.url} alt={title + extra} loading="lazy" />;
}
