/**
 * EntryFormModal: the entry form in a window in the middle of the screen,
 * over the current page, so adding or editing never takes you away from
 * what you were looking at. Opens on `?add` or `?edit=<id>` (see
 * useEntryFormParam); Escape, the thin × in its top corner or "cancel" put
 * it away. The window itself is the shared PaperWindow (resizable, rising
 * in and sinking out). While the entry to edit is on its way it says "loading".
 *
 * A new entry goes into the board you were looking at (/b/<slug>, or home)
 * unless you pick another. Mounted once for the whole site in App.tsx, and
 * only for the owner.
 * After a save it tells the open page to reload (entrySavedEvent).
 */

import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { fetchBoards } from "../../api/boardsApi";
import { fetchEntry } from "../../api/entriesApi";
import { isOwnerSignedIn } from "../../api/ownerSignIn";
import { LoadingWord } from "../../components/LoadingWord";
import { PaperWindow } from "../../components/PaperWindow";
import type { Board, Entry } from "../../types/entry";
import { HOME_BOARD } from "../grid/boardPath";
import { EntryForm } from "./EntryForm";
import { announceEntrySaved } from "./entrySavedEvent";
import { useEntryFormParam } from "./useEntryFormParam";

export function EntryFormModal() {
  const { isAdding, editId, closeEntryForm } = useEntryFormParam();
  // What the window shows. Kept while it lifts away, so it doesn't go blank mid-animation.
  const [shown, setShown] = useState<{ entry: Entry | null } | null>(null);
  const isOpen = isOwnerSignedIn() && (isAdding || editId !== null);
  const [boards, setBoards] = useState<Board[]>([]);
  const pageBoard = useLocation().pathname.match(/^\/b\/([^/]+)/)?.[1] ?? HOME_BOARD;

  useEffect(() => {
    if (isOpen) fetchBoards().then(setBoards).catch(console.error);
  }, [isOpen]);

  useEffect(() => {
    if (isAdding) setShown({ entry: null });
    if (editId)
      fetchEntry(editId)
        .then((entry) => setShown({ entry }))
        .catch(closeEntryForm);
    // Only a new request should refetch (closeEntryForm is a new function every render).
  }, [isAdding, editId]);

  return (
    <PaperWindow
      open={isOpen}
      title={shown?.entry || editId ? "Edit entry" : "Add an entry"}
      onClose={closeEntryForm}
      onClosed={() => setShown(null)}
    >
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
    </PaperWindow>
  );
}
