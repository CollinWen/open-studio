/**
 * sphereLayout: where each entry floats in the sphere view. Every entry sits
 * on the surface of one orb, spread evenly, in time order from top to
 * bottom: the newest at the top pole, the oldest at the bottom. So each year
 * is a band around the orb, like a line of latitude.
 *
 * Used by SphereView. Positions are on a sphere of radius 1 (y is down, as
 * on screen); turning and drawing them in perspective is sphereMotion.ts.
 */

import type { Entry } from "../../types/entry";
import { yearOf } from "./entryHighlight";

export interface SpherePosition {
  x: number;
  y: number;
  z: number;
}

export interface SpherePoint extends SpherePosition {
  entry: Entry;
}

export interface SphereLayout {
  points: SpherePoint[];
  /** Each year's average height on the orb, so the view can turn that band to face you. */
  yearHeights: Map<string, number>;
}

const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

export function layOutSphere(entries: Entry[]): SphereLayout {
  const newestFirst = [...entries].sort((a, b) => b.occurred_at.localeCompare(a.occurred_at));
  const points = newestFirst.map((entry, i) => ({ entry, ...spiralPosition(i, newestFirst.length) }));

  const heightsByYear = new Map<string, number[]>();
  for (const point of points) {
    const year = yearOf(point.entry);
    heightsByYear.set(year, [...(heightsByYear.get(year) ?? []), point.y]);
  }
  const yearHeights = new Map(
    [...heightsByYear].map(([year, heights]) => [year, heights.reduce((sum, h) => sum + h, 0) / heights.length]),
  );
  return { points, yearHeights };
}

/** The i-th of `count` points down a spiral from top pole to bottom: an even spread for any count. */
function spiralPosition(i: number, count: number): SpherePosition {
  const y = count === 1 ? 0 : -1 + (2 * (i + 0.5)) / count;
  const ring = Math.sqrt(1 - y * y);
  const angle = i * GOLDEN_ANGLE;
  return { x: Math.cos(angle) * ring, y, z: Math.sin(angle) * ring };
}
