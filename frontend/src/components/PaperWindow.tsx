/**
 * PaperWindow: a window of paper in the middle of the screen, over the
 * current page, edged by a thin rule, with a title and a thin × in its top
 * corner. Escape or the × asks to close it (onClose); it rises in, sinks out,
 * and tells onClosed once it has gone, so its contents can stay put while it
 * leaves. Drag its bottom-right corner to make it bigger or smaller.
 *
 * Knows nothing of what's inside. The entry form opens in one
 * (EntryFormModal), and so do the studio's agent and token windows.
 * Looks: .paper-window in styles/paper-window.css.
 */

import { useEffect, useRef, type ReactNode } from "react";
import { Icon } from "./Icon";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  /** Called once the window has finished leaving. */
  onClosed?: () => void;
  children: ReactNode;
}

export function PaperWindow({ open, title, onClose, onClosed, children }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (open) {
      // Reopened mid-lift: stop lifting.
      element.classList.remove("is-closing");
      if (!element.open) element.showModal();
    }
    if (!open && element.open) {
      // Let the window lift away before it's taken off the page.
      element.classList.add("is-closing");
      const finish = (event: AnimationEvent) => {
        // Its own lines animate too; only the window's ending counts.
        if (event.target !== element) return;
        element.classList.remove("is-closing");
        element.close();
        onClosed?.();
      };
      element.addEventListener("animationend", finish);
      return () => element.removeEventListener("animationend", finish);
    }
  }, [open]);

  return (
    <dialog
      ref={dialog}
      className="paper-window"
      aria-label={title}
      // Escape asks to close; the owner of the window decides, so it can animate out.
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className="paper-window-top">
        <p className="paper-window-title">{title}</p>
        <button type="button" className="icon-button paper-window-close" aria-label="close" onClick={onClose}>
          <Icon name="close" />
        </button>
      </div>
      {children}
    </dialog>
  );
}
