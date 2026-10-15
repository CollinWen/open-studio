/**
 * SphereView: the "sphere" view, the home page's default. Every entry's
 * cover picture floats on the surface of one orb, in time order: newest at
 * the top, oldest at the bottom, so each year is a band around it. The orb
 * turns slowly; drag to spin it. Picking years (the Years row) turns the
 * middle of their bands to face you and fades the rest; picking a tag fades what
 * doesn't match. Hovering a picture holds it still, enlarges it, dims the
 * rest and shows its title and date; clicking opens the entry. Entries with
 * no picture float as their title.
 *
 * Used by HomePage. Where things sit: sphereLayout.ts. Turning and
 * perspective: sphereMotion.ts. Every item is a plain link, so this works
 * in any browser and with a keyboard.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import type { Entry } from "../../types/entry";
import { formatDate } from "../entries/formatDate";
import { EntryCover } from "./EntryCover";
import { isFaded, type Highlight } from "./entryHighlight";
import { layOutSphere } from "./sphereLayout";
import { createSpin, projectPoint, stepSpin, tiltFacing } from "./sphereMotion";

interface Props {
  entries: Entry[];
  highlight: Highlight;
}

/** How much a hovered picture grows. */
const HOVER_GROWTH = 2.2;
/** How strongly pictures that don't match the picked tag or year still show. */
const FADED_OPACITY = 0.08;
/** A drag farther than this (in pixels) is a spin, not a click. */
const CLICK_SLOP = 6;
/** While one picture is hovered, the rest dim to this share of their opacity so its label reads clearly. */
const SPOTLIGHT_DIM = 0.15;
const DRAG_SPEED = 0.006;
const LABEL_OFFSET = 18;

export function SphereView({ entries, highlight }: Props) {
  const stageRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<(HTMLAnchorElement | null)[]>([]);
  const labelRef = useRef<HTMLDivElement>(null);
  const highlightRef = useRef(highlight);
  const spinRef = useRef(createSpin());
  const { points, yearHeights } = useMemo(() => layOutSphere(entries), [entries]);
  const [hovered, setHovered] = useState<number | null>(null);
  const hoveredRef = useRef<number | null>(null);

  highlightRef.current = highlight;
  hoveredRef.current = hovered;

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const spin = spinRef.current;
    const growth = points.map(() => 1);
    const drag = { active: false, x: 0, y: 0, moved: 0 };
    let leanTarget = 0;

    const onDown = (event: PointerEvent) =>
      Object.assign(drag, { active: true, x: event.clientX, y: event.clientY, moved: 0 });
    const onMove = (event: PointerEvent) => {
      const bounds = stage.getBoundingClientRect();
      leanTarget = ((event.clientY - bounds.top) / bounds.height - 0.5) * 0.35;
      const label = labelRef.current;
      if (label) {
        const x = event.clientX - bounds.left;
        const flip = x > bounds.width - 240;
        label.style.transform = `translate(${x + (flip ? -LABEL_OFFSET : LABEL_OFFSET)}px, ${event.clientY - bounds.top + LABEL_OFFSET}px) translateX(${flip ? "-100%" : "0"})`;
      }
      if (!drag.active) return;
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      drag.moved += Math.abs(dx) + Math.abs(dy);
      spin.turnSpeed = dx * DRAG_SPEED;
      spin.tiltSpeed = dy * DRAG_SPEED;
      Object.assign(drag, { x: event.clientX, y: event.clientY });
    };
    const onUp = () => (drag.active = false);
    // After a spin, the pointer lands on a link; don't let that count as a click.
    const onClick = (event: MouseEvent) => {
      if (drag.moved > CLICK_SLOP) event.preventDefault();
      drag.moved = 0; // so a later keyboard Enter, which has no pointerdown, still opens the entry
    };
    stage.addEventListener("pointerdown", onDown);
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    stage.addEventListener("click", onClick, true);

    let frame = 0;
    const tick = () => {
      const width = stage.clientWidth;
      const height = stage.clientHeight;
      const baseSize = Math.min(120, Math.max(36, (Math.min(width, height) * 0.5) / Math.sqrt(points.length)));
      const bandHeights = highlightRef.current.years.flatMap((year) => yearHeights.get(year) ?? []);
      const bandHeight =
        bandHeights.length === 0 ? undefined : bandHeights.reduce((sum, h) => sum + h, 0) / bandHeights.length;
      spin.tiltTarget = bandHeight === undefined ? null : tiltFacing(bandHeight);
      stepSpin(spin, hoveredRef.current !== null || drag.active, drag.active, calm);
      spin.lean += (leanTarget - spin.lean) * 0.04;

      points.forEach((point, i) => {
        const item = itemRefs.current[i];
        if (!item) return;
        const screen = projectPoint(point, spin, width, height);
        const isHovered = hoveredRef.current === i;
        growth[i] += ((isHovered ? HOVER_GROWTH : 1) - growth[i]) * 0.18;
        const faded = isFaded(point.entry, highlightRef.current);
        item.style.width = `${baseSize * screen.scale * growth[i]}px`;
        item.style.transform = `translate3d(${screen.x}px, ${screen.y}px, 0) translate(-50%, -50%)`;
        const dimmed = hoveredRef.current !== null && !isHovered ? SPOTLIGHT_DIM : 1;
        item.style.opacity = String(faded ? FADED_OPACITY : isHovered ? 1 : (0.3 + 0.7 * screen.nearness) * dimmed);
        item.style.zIndex = String(isHovered ? 10000 : Math.round(screen.nearness * 1000));
      });
      frame = requestAnimationFrame(tick);
    };
    tick();

    return () => {
      cancelAnimationFrame(frame);
      stage.removeEventListener("pointerdown", onDown);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      stage.removeEventListener("click", onClick, true);
    };
  }, [points, yearHeights]);

  const hoveredEntry = hovered === null ? null : points[hovered].entry;

  return (
    <div ref={stageRef} className="sphere-view">
      {points.map(({ entry }, i) => (
        <Link
          key={entry.id}
          ref={(element) => {
            itemRefs.current[i] = element;
          }}
          to={`/entry/${entry.id}`}
          className="sphere-item"
          draggable={false}
          onPointerEnter={() => setHovered(i)}
          onPointerLeave={() => setHovered((current) => (current === i ? null : current))}
          onFocus={() => setHovered(i)}
          onBlur={() => setHovered(null)}
        >
          {entry.media.length > 0 ? <EntryCover media={entry.media} title={entry.title} /> : <span>{entry.title}</span>}
        </Link>
      ))}
      <div ref={labelRef} className={hoveredEntry ? "sphere-label is-visible" : "sphere-label"} aria-hidden="true">
        {hoveredEntry && (
          <>
            <span>{hoveredEntry.title}</span>
            <span className="quiet">
              {hoveredEntry.kind} · {formatDate(hoveredEntry.occurred_at)}
            </span>
          </>
        )}
      </div>
    </div>
  );
}
