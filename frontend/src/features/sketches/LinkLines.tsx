/**
 * LinkLines: the threads drawn over the contact sheet, one gently curved
 * line from the middle of one picture to the middle of another, with a dot
 * at each end. Drawn white with "difference" blending, so a thread is black
 * on the paper and shows as a negative over a photo (like the cursor).
 *
 * Used by ContactSheet. Knows nothing about entries; just tiles and pairs.
 */

import type { Tile } from "./justifyRows";

export interface Thread {
  from: Tile;
  to: Tile;
  /** Faint threads sit in the background; strong ones belong to the hovered picture. */
  strong: boolean;
}

/** How far a thread bows sideways, as a share of its length. */
const BOW = 0.18;

export function LinkLines({ threads, width, height }: { threads: Thread[]; width: number; height: number }) {
  return (
    <svg className="link-lines" width={width} height={height} aria-hidden="true">
      {threads.map(({ from, to, strong }, i) => {
        const [x1, y1] = middleOf(from);
        const [x2, y2] = middleOf(to);
        // Bow to one side, consistently, so crossing threads read as separate strands.
        const bendX = (x1 + x2) / 2 - (y2 - y1) * BOW;
        const bendY = (y1 + y2) / 2 + (x2 - x1) * BOW;
        return (
          <g key={i} className={strong ? "link-line is-strong" : "link-line"}>
            <path d={`M ${x1} ${y1} Q ${bendX} ${bendY} ${x2} ${y2}`} />
            <circle cx={x1} cy={y1} r={2.5} />
            <circle cx={x2} cy={y2} r={2.5} />
          </g>
        );
      })}
    </svg>
  );
}

function middleOf(tile: Tile): [number, number] {
  return [tile.x + tile.width / 2, tile.y + tile.height / 2];
}
