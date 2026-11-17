/**
 * EntryPage ( /entry/:id ): one entry on its own. The title set large, then
 * two columns: a narrow one with every fact about the entry (the wall label:
 * board, kind, date, source, tags), and a wide one to read: the notes, then
 * every picture and write-up. Related entries follow underneath.
 * The large studio mark holds the page until the entry itself arrives.
 * The owner also sees "edit" at the top of the wall label (it opens the
 * entry form over this page, ?edit=<id>, and the page reloads after a save),
 * and a quiet row at the foot saying what the studio read (EntryReading).
 */

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchEntry, fetchRelatedEntries } from "../api/entriesApi";
import { isOwnerSignedIn } from "../api/ownerSignIn";
import { LabelRow } from "../components/LabelRow";
import { LoadingMark } from "../components/LoadingMark";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { EntryReading } from "../features/entries/EntryReading";
import { EntryNotes } from "../features/entries/EntryNotes";
import { MediaSeries } from "../features/entries/MediaSeries";
import { RelatedEntries } from "../features/entries/RelatedEntries";
import { WallLabel } from "../features/entries/WallLabel";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import type { Entry } from "../types/entry";

export function EntryPage() {
  const { id = "" } = useParams();
  const [entry, setEntry] = useState<Entry | null>(null);
  // null while on its way.
  const [related, setRelated] = useState<Entry[] | null>(null);
  const [missing, setMissing] = useState(false);

  const load = useCallback(() => {
    setMissing(false);
    fetchEntry(id)
      .then(setEntry)
      .catch(() => setMissing(true));
    fetchRelatedEntries(id)
      .then(setRelated)
      .catch(() => setRelated([]));
  }, [id]);

  useEffect(() => {
    setEntry(null);
    setRelated(null);
    load();
  }, [load]);
  useOnEntrySaved(load);

  return (
    <>
      <SiteHeader />
      <main>
        {!missing && !entry && <LoadingMark />}
        {missing && (
          <LabelRow rule="double">
            <p className="quiet">Nothing here.</p>
          </LabelRow>
        )}
        {entry && (
          <>
            <LabelRow rule="double" className="intro-row">
              <h1 className="display">{entry.title}</h1>
            </LabelRow>
            <LabelRow>
              <div className="entry-layout">
                <aside className="entry-aside">
                  <WallLabel
                    entry={entry}
                    ownerActions={
                      isOwnerSignedIn() && (
                        <p className="word-list">
                          <Link to={`?edit=${entry.id}`}>edit</Link>
                          <span className="quiet">{entry.visibility}</span>
                        </p>
                      )
                    }
                  />
                </aside>
                <div className="entry-main">
                  <EntryNotes text={entry.description} />
                  <MediaSeries media={entry.media} title={entry.title} />
                </div>
              </div>
            </LabelRow>
            <RelatedEntries entries={related ?? []} />
            {isOwnerSignedIn() && (
              // A new key after each save (updated_at), so it checks again whether a reading is under way.
              <EntryReading key={entry.updated_at} entryId={entry.id} onReadingDone={load} />
            )}
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
