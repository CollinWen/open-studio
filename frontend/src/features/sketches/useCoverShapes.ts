/**
 * useCoverShapes: each entry's cover shape (width ÷ height), found by
 * loading the picture. Until a picture loads it counts as 4:3; entries
 * without a picture are a fixed shape for their title.
 *
 * Used by ContactSheet, so the sheet can lay pictures out at their real shapes.
 */

import { useEffect, useState } from "react";
import type { Entry } from "../../types/entry";

const UNKNOWN_SHAPE = 4 / 3;
const TITLE_ONLY_SHAPE = 1.1;

export function useCoverShapes(entries: Entry[]): Map<string, number> {
  const [shapes, setShapes] = useState(() => new Map<string, number>());

  useEffect(() => {
    let cancelled = false;
    for (const entry of entries) {
      const cover = entry.media[0];
      const source = cover && (cover.thumbnail_url || (cover.type === "image" ? cover.url : ""));
      if (!source) continue;
      const image = new Image();
      image.onload = () => {
        if (cancelled || !image.naturalHeight) return;
        setShapes((current) => new Map(current).set(entry.id, image.naturalWidth / image.naturalHeight));
      };
      image.src = source;
    }
    return () => {
      cancelled = true;
    };
  }, [entries]);

  return new Map(entries.map((entry) => [entry.id, shapes.get(entry.id) ?? (entry.media.length ? UNKNOWN_SHAPE : TITLE_ONLY_SHAPE)]));
}
