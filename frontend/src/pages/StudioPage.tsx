/**
 * StudioPage ( /studio ): the owner's back room.
 * Asks for the owner token once, then lists the boards (add one, change its
 * name or brief), every entry to edit or delete, every tag to describe and
 * rank, then the agents (add, pause, re-key, remove, and which boards each
 * may add to). Adding and editing happen in the
 * entry form that opens over the page (?add, ?edit=<id>; see
 * features/studio/EntryFormModal.tsx), so this page only has to list.
 * Linked as "owner" (or "studio", once signed in) in the header.
 */

import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchEntries } from "../api/entriesApi";
import { forgetOwnerToken, readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "../components/LabelRow";
import { SiteHeader } from "../components/SiteHeader";
import { AgentManager } from "../features/studio/AgentManager";
import { BoardManager } from "../features/studio/BoardManager";
import { EntryIndex } from "../features/studio/EntryIndex";
import { OwnerTokenForm } from "../features/studio/OwnerTokenForm";
import { TagNotesEditor } from "../features/studio/TagNotesEditor";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import { useEntryFormParam } from "../features/studio/useEntryFormParam";
import type { Entry } from "../types/entry";

export function StudioPage() {
  const [hasToken, setHasToken] = useState(Boolean(readOwnerToken()));
  const [entries, setEntries] = useState<Entry[]>([]);
  // Bumped when a board is added, so the agents list shows it as a board to sign agents on to.
  const [boardsAdded, setBoardsAdded] = useState(0);
  const { openEntryEdit } = useEntryFormParam();

  const reload = useCallback(() => {
    fetchEntries().then(setEntries).catch(console.error);
  }, []);

  useEffect(() => {
    if (hasToken) reload();
  }, [hasToken, reload]);
  useOnEntrySaved(reload);

  if (!hasToken) {
    return (
      <>
        <SiteHeader />
        <main>
          <LabelRow rule="double" label="Studio">
            <OwnerTokenForm onSaved={() => setHasToken(true)} />
          </LabelRow>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteHeader>
        <button
          type="button"
          onClick={() => {
            forgetOwnerToken();
            setHasToken(false);
          }}
        >
          leave
        </button>
      </SiteHeader>
      <main>
        <LabelRow rule="double" label="Studio">
          <p className="word-list">
            <Link to="?add">add an entry</Link>
            <span className="quiet">
              {entries.length} entries · {entries.filter((entry) => entry.visibility !== "public").length} not
              public yet
            </span>
          </p>
        </LabelRow>
        <LabelRow rule="single" label="Boards">
          <BoardManager onAdded={() => setBoardsAdded((count) => count + 1)} />
        </LabelRow>
        <LabelRow rule="single" label="Entries">
          <EntryIndex entries={entries} onEdit={(entry) => openEntryEdit(entry.id)} onChanged={reload} />
        </LabelRow>
        <LabelRow rule="single" label="Tags">
          <TagNotesEditor key={entries.length} />
        </LabelRow>
        <LabelRow rule="single" label="Agents">
          <AgentManager key={boardsAdded} />
        </LabelRow>
      </main>
    </>
  );
}
