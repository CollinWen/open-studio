/**
 * ContactSheet: entries as a tight proof sheet, pictures at their own shapes
 * packed edge to edge in rows, with threads drawn between related entries.
 * How threads show depends on the sketch:
 *
 *   hover     only the hovered picture's threads; everything unrelated dims
 *             (nothing dims when the hovered entry has no relatives)
 *   threads   every thread, faintly, all the time; hovering brings one forward
 *   kinship   one thread running through the sheet's order (related work sits together)
 *
 * Used by SketchPage. Layout math: justifyRows.ts. Drawing threads: LinkLines.tsx.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import type { Entry } from "../../types/entry";
import { formatDate } from "../entries/formatDate";
import { EntryCover } from "../grid/EntryCover";
import { justifyRows } from "./justifyRows";
import { LinkLines, type Thread } from "./LinkLines";
import type { Link } from "./relatedLinks";
import { useCoverShapes } from "./useCoverShapes";

export type ThreadStyle = "hover" | "threads" | "kinship";

interface Props {
  entries: Entry[];
  links: Link[];
  threadStyle: ThreadStyle;
  rowHeight: number;
  gap: number;
}

const LABEL_OFFSET = 16;

export function ContactSheet({ entries, links, threadStyle, rowHeight, gap }: Props) {
  const sheetRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [hovered, setHovered] = useState<string | null>(null);
  const shapes = useCoverShapes(entries);

  useEffect(() => {
    const sheet = sheetRef.current;
    if (!sheet) return;
    const observer = new ResizeObserver(() => setWidth(sheet.clientWidth));
    observer.observe(sheet);
    return () => observer.disconnect();
  }, []);

  // Shapes as text, so the layout is only redone when a shape actually changes.
  const shapeKey = entries.map((entry) => shapes.get(entry.id)).join(",");
  const layout = useMemo(() => justifyRows(shapeKey.split(",").map(Number), width, rowHeight, gap), [shapeKey, width, rowHeight, gap]);
  const tileOf = new Map(entries.map((entry, i) => [entry.id, layout.tiles[i]]));

  const neighbours = new Set(hovered ? links.flatMap((link) => (link.from === hovered ? [link.to] : link.to === hovered ? [link.from] : [])) : []);
  const touchesHovered = (link: Link) => link.from === hovered || link.to === hovered;
  const threads: Thread[] = pickThreads(entries, links, threadStyle, hovered)
    .filter((link) => tileOf.get(link.from) && tileOf.get(link.to))
    .map((link) => ({ from: tileOf.get(link.from)!, to: tileOf.get(link.to)!, strong: touchesHovered(link) || (threadStyle === "kinship" && !hovered) }));
  const hoveredEntry = entries.find((entry) => entry.id === hovered);

  const moveLabel = (event: React.PointerEvent) => {
    const label = labelRef.current;
    const sheet = sheetRef.current;
    if (!label || !sheet) return;
    const bounds = sheet.getBoundingClientRect();
    const x = event.clientX - bounds.left;
    const flip = x > bounds.width - 260;
    label.style.transform = `translate(${x + (flip ? -LABEL_OFFSET : LABEL_OFFSET)}px, ${event.clientY - bounds.top + LABEL_OFFSET}px) translateX(${flip ? "-100%" : "0"})`;
  };

  return (
    <div ref={sheetRef} className="contact-sheet" style={{ height: layout.height }} onPointerMove={moveLabel}>
      {width > 0 &&
        entries.map((entry, i) => {
          const tile = layout.tiles[i];
          const dim = neighbours.size > 0 && hovered !== entry.id && !neighbours.has(entry.id);
          return (
            <RouterLink
              key={entry.id}
              to={`/entry/${entry.id}`}
              className={dim ? "sheet-tile is-dim" : "sheet-tile"}
              // Title-only tiles set their type in proportion to the row, so small rows stay legible.
              style={{ left: tile.x, top: tile.y, width: tile.width, height: tile.height, fontSize: Math.min(24, Math.max(12, tile.height * 0.1)) }}
              onPointerEnter={() => setHovered(entry.id)}
              onPointerLeave={() => setHovered((current) => (current === entry.id ? null : current))}
            >
              {entry.media.length > 0 ? <EntryCover media={entry.media} title={entry.title} /> : <span>{entry.title}</span>}
            </RouterLink>
          );
        })}
      <LinkLines threads={threads} width={width} height={layout.height} />
      <div ref={labelRef} className={hoveredEntry ? "sheet-label is-visible" : "sheet-label"} aria-hidden="true">
        {hoveredEntry && (
          <>
            <span>{hoveredEntry.title}</span>
            <span>
              {hoveredEntry.kind} · {formatDate(hoveredEntry.occurred_at)}
            </span>
          </>
        )}
      </div>
    </div>
  );
}

/** Which links to draw for this sketch. */
function pickThreads(entries: Entry[], links: Link[], threadStyle: ThreadStyle, hovered: string | null): Link[] {
  const ofHovered = links.filter((link) => link.from === hovered || link.to === hovered);
  if (threadStyle === "hover") return ofHovered;
  if (threadStyle === "threads") return links;
  // Kinship: a thread between neighbours in the order whenever they're related.
  const related = new Set(links.map((link) => [link.from, link.to].sort().join("|")));
  const chain = entries.slice(1).flatMap((entry, i) => {
    const previous = entries[i];
    return related.has([previous.id, entry.id].sort().join("|")) ? [{ from: previous.id, to: entry.id, rank: 0 }] : [];
  });
  return [...chain, ...ofHovered];
}
