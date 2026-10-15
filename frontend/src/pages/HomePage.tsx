/**
 * HomePage ( / ): the whole collection, laid out as labeled rows. The intro
 * set large, the tags, the years, the browse controls (search, view, sort),
 * then the entries: on an orb by default, or as a grid or rows. A picked tag
 * or year highlights its entries in whichever view is showing.
 *
 * Every choice lives in the URL (see useBrowseParams), so any view can be
 * shared or linked to. Selecting a tag swaps the intro for that tag's
 * description.
 */

import { useEffect, useMemo, useState } from "react";
import { fetchEntries } from "../api/entriesApi";
import { searchEntries } from "../api/searchApi";
import { fetchTags } from "../api/tagsApi";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { BrowseControls } from "../features/grid/BrowseControls";
import { EntryGrid } from "../features/grid/EntryGrid";
import { EntryRows } from "../features/grid/EntryRows";
import { SphereView } from "../features/grid/SphereView";
import { sortEntries } from "../features/grid/sortEntries";
import { TagFilter } from "../features/grid/TagFilter";
import { YearFilter } from "../features/grid/YearFilter";
import { yearOf } from "../features/grid/entryHighlight";
import { useBrowseParams } from "../features/grid/useBrowseParams";
import type { Entry, Tag } from "../types/entry";

const INTRO = "A working collection of things I make and things I'm curious about.";

export function HomePage() {
  const { tag, year, query, view, sort, defaultSort, setParam } = useBrowseParams();
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);

  useEffect(() => {
    fetchTags().then(setTags).catch(console.error);
  }, []);

  useEffect(() => {
    const load = query ? searchEntries(query) : fetchEntries();
    load.then(setEntries).catch(() => setEntries([]));
  }, [query]);

  const activeTag = tags.find((candidate) => candidate.name === tag);
  const intro = tag ? activeTag?.description || `Everything tagged “${tag}”.` : INTRO;
  // Kept stable between renders so the sphere doesn't rebuild on every hover.
  const shown = useMemo(() => entries && sortEntries(entries, sort), [entries, sort]);

  const years = useMemo(() => [...new Set(entries?.map(yearOf))].sort().reverse(), [entries]);
  const highlight = useMemo(() => ({ tag, year }), [tag, year]);

  return (
    <>
      <SiteHeader>{entries && `${entries.length} ${entries.length === 1 ? "entry" : "entries"}`}</SiteHeader>
      <main>
        <LabelRow rule="double" label={tag ? "Tag" : "Open Studio"} className="intro-row">
          <p className="display">{intro}</p>
        </LabelRow>
        <LabelRow rule="single" label="Tags">
          <TagFilter tags={tags} activeTag={tag} onSelect={(name) => setParam("tag", name)} />
        </LabelRow>
        <LabelRow rule="single" label="Years">
          <YearFilter years={years} activeYear={year} onSelect={(picked) => setParam("year", picked)} />
        </LabelRow>
        <LabelRow rule="single" label="View">
          <BrowseControls query={query} view={view} sort={sort} defaultSort={defaultSort} onChange={setParam} />
        </LabelRow>
        <LabelRow rule="double" wide label="Index">
          {shown?.length === 0 && <p className="quiet">{query ? "Nothing matches that." : "Nothing here yet."}</p>}
          {shown && view === "sphere" && shown.length > 0 && <SphereView entries={shown} highlight={highlight} />}
          {shown && view === "rows" && <EntryRows entries={shown} highlight={highlight} />}
          {shown && view !== "rows" && view !== "sphere" && (
            <EntryGrid entries={shown} highlight={highlight} size={view} />
          )}
        </LabelRow>
      </main>
      <SiteFooter />
    </>
  );
}
