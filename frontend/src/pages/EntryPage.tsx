/**
 * EntryPage ( /entry/:id ): one entry on its own, as labeled rows: the wall
 * label (title, kind, date, source, notes), tags, every picture, then
 * related entries.
 * The owner also sees an "edit" link that opens it in the studio page.
 */

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchEntry, fetchRelatedEntries } from "../api/entriesApi";
import { readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { EntryTags } from "../features/entries/EntryTags";
import { MediaSeries } from "../features/entries/MediaSeries";
import { RelatedEntries } from "../features/entries/RelatedEntries";
import { WallLabel } from "../features/entries/WallLabel";
import type { Entry } from "../types/entry";

export function EntryPage() {
  const { id = "" } = useParams();
  const [entry, setEntry] = useState<Entry | null>(null);
  const [related, setRelated] = useState<Entry[]>([]);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    setEntry(null);
    setMissing(false);
    fetchEntry(id)
      .then(setEntry)
      .catch(() => setMissing(true));
    fetchRelatedEntries(id)
      .then(setRelated)
      .catch(() => setRelated([]));
  }, [id]);

  return (
    <>
      <SiteHeader>{entry && readOwnerToken() && <Link to={`/studio?edit=${entry.id}`}>edit</Link>}</SiteHeader>
      <main>
        {missing && (
          <LabelRow rule="double" label="Entry">
            <p className="quiet">Nothing here.</p>
          </LabelRow>
        )}
        {entry && (
          <>
            <WallLabel entry={entry} />
            <EntryTags tags={entry.tags} />
            {entry.media.length > 0 && (
              <LabelRow rule="double" label="Media">
                <MediaSeries media={entry.media} title={entry.title} />
              </LabelRow>
            )}
            <RelatedEntries entries={related} />
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
