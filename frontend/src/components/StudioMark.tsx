/**
 * StudioMark: the site's logo, a small panel of dots. Read across, its dots
 * make a C and a W; turned on its side, it looks like a display panel of lit
 * numbers. Drawn from MARK_PATTERN below, so changing the rows there redraws
 * it everywhere (the favicon in public/favicon.svg is a copy; redraw it too,
 * and ios/Shared/StudioMark.swift draws the same pattern for the phone).
 *
 * While something is on its way (`playing`), the dots light up in a sweep
 * from the top-left corner and fade again, like a panel refreshing. Used by
 * LoadingWord, LoadingMark and the footer.
 *
 * Looks: .studio-mark in global.css (dot ink, sizes, the sweep).
 */

import type { CSSProperties } from "react";

// "O" is a lit dot, "_" an empty place. Every row the same length.
export const MARK_PATTERN = ["_O_O_", "O_O_O", "O_O_O", "_O_O_"];

// Each dot sits in a 1 × 1 cell; its radius leaves a gap around it.
const DOT_RADIUS = 0.36;

const DOTS = MARK_PATTERN.flatMap((row, y) =>
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
      {DOTS.map(({ x, y }) => (
        <circle
          key={`${x}-${y}`}
          cx={x + 0.5}
          cy={y + 0.5}
          r={DOT_RADIUS}
          // The sweep: a dot lights later the further it is from the top-left corner.
          style={{ "--mark-order": x + y } as CSSProperties}
        />
      ))}
    </svg>
  );
}
