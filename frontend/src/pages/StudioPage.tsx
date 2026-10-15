/**
 * StudioPage ( /studio ): the owner's back room.
 * Asks for the owner token once, then shows the entry form and a list of
 * every entry to edit or delete, then every tag to describe and rank.
 * Linked as "owner" in the footer.
 * /studio?edit=<id> opens that entry in the form (the "edit" link on entry pages).
 */

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchEntries } from "../api/entriesApi";
import { forgetOwnerToken, readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "../components/LabelRow";
import { SiteHeader } from "../components/SiteHeader";
import { EntryForm } from "../features/studio/EntryForm";
import { EntryIndex } from "../features/studio/EntryIndex";
import { OwnerTokenForm } from "../features/studio/OwnerTokenForm";
import { TagNotesEditor } from "../features/studio/TagNotesEditor";
import type { Entry } from "../types/entry";

export function StudioPage() {
  const [hasToken, setHasToken] = useState(Boolean(readOwnerToken()));
  const [entries, setEntries] = useState<Entry[]>([]);
  const [editing, setEditing] = useState<Entry | null>(null);
  // Changing this key resets the form to blank after a save or cancel.
  const [formKey, setFormKey] = useState(0);
  const [searchParams, setSearchParams] = useSearchParams();
  const editId = searchParams.get("edit");

  const reload = useCallback(() => {
    fetchEntries().then(setEntries).catch(console.error);
  }, []);

  useEffect(() => {
    if (hasToken) reload();
  }, [hasToken, reload]);

  // Arriving from an entry's "edit" link: open that entry once the list has loaded.
  useEffect(() => {
    const match = entries.find((entry) => entry.id === editId);
    if (match) setEditing(match);
  }, [entries, editId]);

  const resetForm = () => {
    setEditing(null);
    setSearchParams({});
    setFormKey((key) => key + 1);
  };

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
        <LabelRow rule="double" label={editing ? "Edit" : "Add"}>
          <EntryForm
            key={editing?.id ?? `new-${formKey}`}
            editing={editing}
            onSaved={() => {
              resetForm();
              reload();
            }}
            onCancel={resetForm}
          />
        </LabelRow>
        <LabelRow rule="single" label="Entries">
          <EntryIndex
            entries={entries}
            onEdit={(entry) => {
              setEditing(entry);
              window.scrollTo(0, 0);
            }}
            onChanged={reload}
          />
        </LabelRow>
        <LabelRow rule="single" label="Tags">
          <TagNotesEditor key={entries.length} />
        </LabelRow>
      </main>
    </>
  );
}
