/**
 * LoadingMark: a large studio mark, sweeping, that stands where a view will
 * appear (a board's sphere, an entry's pictures) until its first content
 * arrives, so an empty page reads as "on its way", not "nothing here".
 * Only for the eye: the header's LoadingWord is what screen readers hear.
 *
 * Not here: the small mark and word for the header and forms (LoadingWord.tsx).
 * Looks: .loading-mark in global.css.
 */

import { StudioMark } from "./StudioMark";

export function LoadingMark() {
  return (
    <div className="loading-mark" aria-hidden="true">
      <StudioMark playing size="large" />
    </div>
  );
}
