/**
 * StudioMark: the site's logo, a small panel of squares. Each lit cell is a
 * whole square, so neighbours meet edge to edge or at a corner and the mark
 * reads as one pixel glyph: across, a C and a W; on its side, a display
 * panel. Drawn from MARK_PATTERN below, so changing the rows there redraws it
 * everywhere (the favicon in public/favicon.svg is a copy; redraw it too,
 * and ios/Shared/StudioMark.swift draws the same pattern for the phone).
 *
 * While something is on its way (`playing`), the squares light up in a sweep
 * from the top-left corner and fade again, like a panel refreshing. Used by
 * LoadingWord, LoadingMark and the footer.
 *
 * Looks: .studio-mark in global.css (ink, sizes, the sweep).
 */

import type { CSSProperties } from "react";

// "O" is a lit square, "_" an empty place. Every row the same length.
export const MARK_PATTERN = ["_O_O_", "O_O_O", "O_O_O", "_O_O_"];

// A hair over one cell, so squares that share an edge show no seam between them.
const SQUARE = 1.002;

const SQUARES = MARK_PATTERN.flatMap((row, y) =>
  [...row].flatMap((cell, x) => (cell === "O" ? [{ x, y }] : [])),
);
const WIDTH = MARK_PATTERN[0].length;
const HEIGHT = MARK_PATTERN.length;

interface Props {
  playing?: boolean;
  size?: "small" | "large";
}

export function StudioMark({ playing = false, size = "small" }: Props) {
  return (
    <svg
      className={`studio-mark studio-mark-${size}${playing ? " is-playing" : ""}`}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      aria-hidden="true"
      focusable="false"
    >
      {SQUARES.map(({ x, y }) => (
        <rect
          key={`${x}-${y}`}
          x={x}
          y={y}
          width={SQUARE}
          height={SQUARE}
          // The sweep: a square lights later the further it is from the top-left corner.
          style={{ "--mark-order": x + y } as CSSProperties}
        />
      ))}
    </svg>
  );
}
