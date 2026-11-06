/**
 * LoadingMark: a large studio mark, sweeping, that stands where a view will
 * appear (a board's pictures, an entry's pictures) until its first content
 * arrives, so an empty page reads as "on its way", not "nothing here".
 * Screen readers hear a hidden "loading" instead of the mark.
 *
 * Not here: the small mark and word for the header and forms (LoadingWord.tsx).
 * Looks: .loading-mark in global.css.
 */

import { StudioMark } from "./StudioMark";

export function LoadingMark() {
  return (
    <div className="loading-mark" role="status">
      <StudioMark playing size="large" />
      <span className="visually-hidden">loading</span>
    </div>
  );
}
