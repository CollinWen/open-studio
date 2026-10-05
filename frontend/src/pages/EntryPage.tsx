/**
 * EntryPage ( /entry/:id ): one entry on its own. All its pictures, wall label,
 * tags, and related entries, in a single quiet column.
 * The owner also sees an "edit" link that opens it in the studio page.
 */

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchEntry, fetchRelatedEntries } from "../api/entriesApi";
import { readOwnerToken } from "../api/ownerToken";
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
    fetchEntry(id).then(setEntry).catch(() => setMissing(true));
    fetchRelatedEntries(id).then(setRelated).catch(() => setRelated([]));
  }, [id]);

  return (
    <>
      <SiteHeader>{entry && readOwnerToken() && <Link to={`/studio?edit=${entry.id}`}>edit</Link>}</SiteHeader>
      <main className="column">
        {missing && <p className="quiet">nothing here.</p>}
        {entry && (
          <>
            <MediaSeries media={entry.media} title={entry.title} />
            <WallLabel entry={entry} />
            <EntryTags tags={entry.tags} />
            <RelatedEntries entries={related} />
          </>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
