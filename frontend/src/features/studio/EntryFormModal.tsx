/**
 * EntryFormModal: the entry form in a window in the middle of the screen,
 * over the current page, so adding or editing never takes you away from
 * what you were looking at. Opens on `?add` or `?edit=<id>` (see
 * useEntryFormParam); Escape, the thin × in its top corner or "cancel" put
 * it away. Drag its bottom-right corner to make it bigger or smaller. It
 * rises in and sinks out (.entry-sheet in global.css). While the entry to
 * edit is on its way it says "loading".
 *
 * A new entry goes into the board you were looking at (/b/<slug>, or home)
 * unless you pick another. Mounted once for the whole site in App.tsx, and
 * only for the owner.
 * After a save it tells the open page to reload (entrySavedEvent).
 */

import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { fetchBoards } from "../../api/boardsApi";
import { fetchEntry } from "../../api/entriesApi";
import { isOwnerSignedIn } from "../../api/ownerSignIn";
import { Icon } from "../../components/Icon";
import { LoadingWord } from "../../components/LoadingWord";
import type { Board, Entry } from "../../types/entry";
import { HOME_BOARD } from "../grid/boardPath";
import { EntryForm } from "./EntryForm";
import { announceEntrySaved } from "./entrySavedEvent";
import { useEntryFormParam } from "./useEntryFormParam";

export function EntryFormModal() {
  const { isAdding, editId, closeEntryForm } = useEntryFormParam();
  // What the sheet shows. Kept while it lifts away, so it doesn't go blank mid-animation.
  const [shown, setShown] = useState<{ entry: Entry | null } | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const isOpen = isOwnerSignedIn() && (isAdding || editId !== null);
  const [boards, setBoards] = useState<Board[]>([]);
  const pageBoard = useLocation().pathname.match(/^\/b\/([^/]+)/)?.[1] ?? HOME_BOARD;

  useEffect(() => {
    if (isOpen) fetchBoards().then(setBoards).catch(console.error);
  }, [isOpen]);

  useEffect(() => {
    if (isAdding) setShown({ entry: null });
    if (editId) fetchEntry(editId).then((entry) => setShown({ entry })).catch(closeEntryForm);
    // Only a new request should refetch (closeEntryForm is a new function every render).
  }, [isAdding, editId]);

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (isOpen) {
      // Reopened mid-lift: stop lifting.
      element.classList.remove("is-closing");
      if (!element.open) element.showModal();
    }
    if (!isOpen && element.open) {
      // Let the sheet lift away before it's taken off the page.
      element.classList.add("is-closing");
      const finish = (event: AnimationEvent) => {
        // The form's own lines animate too; only the sheet's ending counts.
        if (event.target !== element) return;
        element.classList.remove("is-closing");
        element.close();
        setShown(null);
      };
      element.addEventListener("animationend", finish);
      return () => element.removeEventListener("animationend", finish);
    }
  }, [isOpen]);

  return (
    <dialog
      ref={dialog}
      className="entry-sheet"
      aria-label={shown?.entry ? "Edit entry" : "Add an entry"}
      // Escape asks to close; going through the URL lets the sheet animate out.
      onCancel={(event) => {
        event.preventDefault();
        closeEntryForm();
      }}
    >
      <div className="entry-sheet-top">
        <p className="entry-sheet-title">{shown?.entry || editId ? "Edit entry" : "Add an entry"}</p>
        <button type="button" className="icon-button entry-sheet-close" aria-label="close" onClick={closeEntryForm}>
          <Icon name="close" />
        </button>
      </div>
      {isOpen && !shown && <LoadingWord />}
      {shown && (
        <EntryForm
          key={shown.entry?.id ?? "new"}
          editing={shown.entry}
          boards={boards}
          defaultBoard={pageBoard}
          onSaved={() => {
            announceEntrySaved();
            closeEntryForm();
          }}
          onCancel={closeEntryForm}
        />
      )}
    </dialog>
  );
}
