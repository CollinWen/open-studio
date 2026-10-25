/**
 * EntryPage ( /entry/:id ): one entry on its own, as labeled rows: the wall
 * label (title, kind, date, source, notes), tags, every picture, then
 * related entries. "loading" breathes in the header until both are in.
 * The owner also sees an Owner row under the title: "edit" opens the entry
 * form over this page (?edit=<id>), and the page reloads after a save.
 */

import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchEntry, fetchRelatedEntries } from "../api/entriesApi";
import { readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "../components/LabelRow";
import { LoadingWord } from "../components/LoadingWord";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { EntryTags } from "../features/entries/EntryTags";
import { MediaSeries } from "../features/entries/MediaSeries";
import { RelatedEntries } from "../features/entries/RelatedEntries";
import { WallLabel } from "../features/entries/WallLabel";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import type { Entry } from "../types/entry";

export function EntryPage() {
  const { id = "" } = useParams();
  const [entry, setEntry] = useState<Entry | null>(null);
  // null while on its way, so the header can say "loading".
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
      <SiteHeader>{!missing && (!entry || !related) && <LoadingWord />}</SiteHeader>
      <main>
        {missing && (
          <LabelRow rule="double" label="Entry">
            <p className="quiet">Nothing here.</p>
          </LabelRow>
        )}
        {entry && (
          <>
            <WallLabel
              entry={entry}
              ownerActions={
                readOwnerToken() && (
                  <p className="word-list">
                    <Link to={`?edit=${entry.id}`}>edit</Link>
                    <span className="quiet">{entry.visibility}</span>
                  </p>
                )
              }
            />
            <EntryTags tags={entry.tags} board={entry.board} />
            {entry.media.length > 0 && (
              <LabelRow rule="double" label="Media">
                <MediaSeries media={entry.media} title={entry.title} />
              </LabelRow>
            )}
            <RelatedEntries entries={related ?? []} />
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
