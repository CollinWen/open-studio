/**
 * CrosshairCursor: replaces the mouse pointer with a small dot that inverts
 * the colors beneath it (black on the white page, a negative over photos).
 * Over anything clickable it grows a little.
 *
 * The inversion is CSS (mix-blend-mode: difference); see .crosshair in
 * global.css. Only used with a mouse: phones and tablets keep their normal
 * touch behavior, and text fields keep the normal typing cursor.
 */

import { useEffect, useRef } from "react";

const CLICKABLE = "a, button, label, [role='button']";
const TEXT_FIELDS = "input, textarea";

export function CrosshairCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const cursor = cursorRef.current;
    if (!cursor || !window.matchMedia("(pointer: fine)").matches) return;

    const onMove = (event: MouseEvent) => {
      const target = event.target as Element;
      cursor.style.transform = `translate(${event.clientX}px, ${event.clientY}px)`;
      cursor.classList.add("is-visible");
      cursor.classList.toggle("is-over-clickable", Boolean(target.closest?.(CLICKABLE)));
      cursor.classList.toggle("is-over-text-field", Boolean(target.closest?.(TEXT_FIELDS)));
    };
    const onLeave = () => cursor.classList.remove("is-visible");

    window.addEventListener("mousemove", onMove);
    document.documentElement.addEventListener("mouseleave", onLeave);
    return () => {
      window.removeEventListener("mousemove", onMove);
      document.documentElement.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return (
    <div ref={cursorRef} className="crosshair" aria-hidden="true">
      <span className="crosshair-shape" />
    </div>
  );
}
