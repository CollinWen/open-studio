/**
 * EntryCover: the picture shown for an entry in the grid. The first media
 * item, using its smaller thumbnail when it has one (so the grid loads fast
 * and embeds like YouTube show a still instead of a player).
 * Videos play silently on loop, like a moving picture, but only while on
 * screen (CoverVideo), fetching just enough to start; pictures
 * fade in as they load. A write-up has no picture, so it has no cover; EntryCard sets
 * its title large instead.
 */

import { FadeInImage } from "../../components/FadeInImage";
import type { MediaItem } from "../../types/entry";
import { CoverVideo } from "./CoverVideo";

export function EntryCover({ media, title }: { media: MediaItem[]; title: string }) {
  const cover = media[0];
  if (!cover || cover.type === "html") return null;
  const extra = media.length > 1 ? ` (+${media.length - 1})` : "";
  if (cover.type === "video" && !cover.thumbnail_url) return <CoverVideo src={cover.url} label={title + extra} />;
  return <FadeInImage className="entry-cover" src={cover.thumbnail_url || cover.url} alt={title + extra} loading="lazy" />;
}
