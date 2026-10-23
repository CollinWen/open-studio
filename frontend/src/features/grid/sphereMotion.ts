/**
 * sphereMotion: how the sphere view turns and how a point in it lands on
 * the screen. The sphere drifts slowly on its own, spins when dragged (and
 * keeps spinning a little after you let go), and tilts gently toward the
 * mouse. When a year is picked it eases its tilt so that year's band faces
 * you. Nearer points are drawn larger and in front of farther ones. While
 * entries are still loading, pictures glide to their new places and new
 * ones emerge (settleToward).
 *
 * Used by SphereView, once per frame. Positions come from sphereLayout.ts.
 */

export interface SphereSpin {
  /** Turn around the vertical axis and tilt toward or away, in radians. */
  turn: number;
  tilt: number;
  turnSpeed: number;
  tiltSpeed: number;
  /** Extra tilt from where the mouse is, eased toward. */
  lean: number;
  /** The tilt to settle at (a picked year's band facing you), or null to tilt freely. */
  tiltTarget: number | null;
}

export interface ScreenPoint {
  x: number;
  y: number;
  /** How large to draw it: 1 at the sphere's middle depth, bigger when nearer. */
  scale: number;
  /** From 0 (farthest) to 1 (nearest). */
  nearness: number;
}

const DRIFT = 0.0018;
const FRICTION = 0.95;
const MAX_TILT = 1.3;
/** Share of the remaining distance to the tilt target covered each frame. */
const SETTLE = 0.06;
/** Camera distance, in sphere radii. Smaller means stronger perspective. */
const CAMERA_DISTANCE = 2.6;

export function createSpin(): SphereSpin {
  return { turn: 0.4, tilt: -0.3, turnSpeed: DRIFT, tiltSpeed: 0, lean: 0, tiltTarget: null };
}

/** The tilt that brings a band at height `y` on the orb (-1 top to 1 bottom) to face you. */
export function tiltFacing(y: number): number {
  return Math.asin(Math.max(-1, Math.min(1, y)));
}

/** Advances one frame. Hovering or dragging holds the drift still so things are easy to click. */
export function stepSpin(spin: SphereSpin, paused: boolean, dragging: boolean, calm: boolean): void {
  const drift = paused || calm ? 0 : DRIFT;
  spin.turnSpeed = drift + (spin.turnSpeed - drift) * FRICTION;
  spin.tiltSpeed *= FRICTION;
  spin.turn += spin.turnSpeed;
  if (spin.tiltTarget !== null && !dragging) {
    spin.tiltSpeed = 0;
    spin.tilt += (spin.tiltTarget - spin.tilt) * (calm ? 1 : SETTLE);
  }
  spin.tilt = Math.max(-MAX_TILT, Math.min(MAX_TILT, spin.tilt + spin.tiltSpeed));
}

/** Turns a point on the unit sphere and projects it onto a screen of the given size. */
export function projectPoint(
  point: { x: number; y: number; z: number },
  spin: SphereSpin,
  width: number,
  height: number,
): ScreenPoint {
  const tilt = spin.tilt + spin.lean;
  const cosTurn = Math.cos(spin.turn);
  const sinTurn = Math.sin(spin.turn);
  const x1 = point.x * cosTurn + point.z * sinTurn;
  const z1 = -point.x * sinTurn + point.z * cosTurn;
  const y2 = point.y * Math.cos(tilt) - z1 * Math.sin(tilt);
  const z2 = point.y * Math.sin(tilt) + z1 * Math.cos(tilt);

  const radius = Math.min(width, height) * 0.42;
  const scale = CAMERA_DISTANCE / (CAMERA_DISTANCE - z2);
  return {
    x: width / 2 + x1 * radius * scale,
    y: height / 2 + y2 * radius * scale,
    scale,
    nearness: (z2 + 1) / 2,
  };
}

// Share of the remaining distance a settling picture covers each frame: quick at first, gentle at the end.
const SETTLE_RATE = 0.08;
const APPEAR_RATE = 0.06;

/** Where a picture is drawn while it eases toward its place, and how far it has emerged (0 to 1). */
export interface SettlingPoint {
  x: number;
  y: number;
  z: number;
  appear: number;
}

/**
 * One frame of a picture easing toward its place on the orb. As more entries
 * load, the spiral spreads over more points and every place shifts a little;
 * pictures glide there along the surface (not through the middle) instead of
 * jumping, slowing as they land. New ones emerge where they belong.
 */
export function settleToward(current: SettlingPoint, target: { x: number; y: number; z: number }, calm: boolean) {
  if (calm) return Object.assign(current, target, { appear: 1 });
  const x = current.x + (target.x - current.x) * SETTLE_RATE;
  const y = current.y + (target.y - current.y) * SETTLE_RATE;
  const z = current.z + (target.z - current.z) * SETTLE_RATE;
  const length = Math.hypot(x, y, z) || 1;
  return Object.assign(current, {
    x: x / length,
    y: y / length,
    z: z / length,
    appear: current.appear + (1 - current.appear) * APPEAR_RATE,
  });
}
