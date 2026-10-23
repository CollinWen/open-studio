/**
 * sphereLayout: where each entry floats in the sphere view. Every entry sits
 * on the surface of one orb, spread evenly, in time order from top to
 * bottom: the newest at the top pole, the oldest at the bottom. So each year
 * is a band around the orb, like a line of latitude, and a picked span of
 * months has a height the view can turn to face (bandHeight).
 *
 * Used by SphereView. Positions are on a sphere of radius 1 (y is down, as
 * on screen); turning and drawing them in perspective is sphereMotion.ts.
 */

import type { Entry } from "../../types/entry";
import { isInRange, monthOf, type MonthRange } from "./monthRange";

export interface SpherePosition {
  x: number;
  y: number;
  z: number;
}

export interface SpherePoint extends SpherePosition {
  entry: Entry;
}

const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

export function layOutSphere(entries: Entry[]): SpherePoint[] {
  const newestFirst = [...entries].sort((a, b) => b.occurred_at.localeCompare(a.occurred_at));
  return newestFirst.map((entry, i) => ({ entry, ...spiralPosition(i, newestFirst.length) }));
}

/** The average height of the entries in a span of months: the band the view turns to face. */
export function bandHeight(points: SpherePoint[], range: MonthRange): number | undefined {
  const heights = points.filter((point) => isInRange(monthOf(point.entry), range)).map((point) => point.y);
  return heights.length === 0 ? undefined : heights.reduce((sum, h) => sum + h, 0) / heights.length;
}

/** The i-th of `count` points down a spiral from top pole to bottom: an even spread for any count. */
function spiralPosition(i: number, count: number): SpherePosition {
  const y = count === 1 ? 0 : -1 + (2 * (i + 0.5)) / count;
  const ring = Math.sqrt(1 - y * y);
  const angle = i * GOLDEN_ANGLE;
  return { x: Math.cos(angle) * ring, y, z: Math.sin(angle) * ring };
}
