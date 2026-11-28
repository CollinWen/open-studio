/**
 * BoardBrief: what a board is for, as the first tile of its work, in place
 * of an intro above it. A visitor reads it beside the pinned entries, so
 * the top of a board says what it is and shows examples at once. With a
 * tag picked it says what that tag means instead.
 *
 * The text is the board's own description (the brief agents read), so it
 * is written in one place, in markdown (MarkdownText). A long one is cut to fit its tile; "read all"
 * opens it to its full length.
 * Used by BoardPage, which hands it to EntryGrid or puts it above rows.
 */

import { useLayoutEffect, useRef, useState } from "react";
import { MarkdownText } from "../../components/MarkdownText";

interface Props {
  label: string;
  text: string;
}

export function BoardBrief({ label, text }: Props) {
  const [open, setOpen] = useState(false);
  const [cut, setCut] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  // Offer "read all" only when the text doesn't fit; checked again as the tile resizes.
  useLayoutEffect(() => {
    const element = textRef.current;
    if (!element || open) return;
    const check = () => setCut(element.scrollHeight > element.clientHeight + 1);
    check();
    const observer = new ResizeObserver(check);
    observer.observe(element);
    return () => observer.disconnect();
  }, [text, open]);

  return (
    <div className={open ? "board-brief is-open" : "board-brief"}>
      <span className="board-brief-label">{label}</span>
      <div ref={textRef} className="board-brief-text">
        <MarkdownText text={text} />
      </div>
      {(cut || open) && (
        <button type="button" className="square quiet board-brief-more" onClick={() => setOpen(!open)}>
          {open ? "less" : "read all"}
        </button>
      )}
    </div>
  );
}
