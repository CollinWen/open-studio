/**
 * HomePage ( / ): the whole collection. An intro line, the tags, a line of
 * browse controls (search, view size, sort), then the entries.
 *
 * Every choice lives in the URL (see useBrowseParams), so any view can be
 * shared or linked to. Selecting a tag swaps the intro for that tag's
 * description.
 */

import { useEffect, useState } from "react";
import { fetchEntries } from "../api/entriesApi";
import { searchEntries } from "../api/searchApi";
import { fetchTags } from "../api/tagsApi";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { BrowseControls } from "../features/grid/BrowseControls";
import { EntryGrid } from "../features/grid/EntryGrid";
import { EntryRows } from "../features/grid/EntryRows";
import { sortEntries } from "../features/grid/sortEntries";
import { TagFilter } from "../features/grid/TagFilter";
import { useBrowseParams } from "../features/grid/useBrowseParams";
import type { Entry, Tag } from "../types/entry";

const INTRO = "A working collection of things I make and things I'm curious about.";

export function HomePage() {
  const { tag, query, view, sort, defaultSort, setParam } = useBrowseParams();
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
  const shown = entries && sortEntries(entries, sort);

  return (
    <>
      <SiteHeader>{entries && `${entries.length} ${entries.length === 1 ? "entry" : "entries"}`}</SiteHeader>
      <main className="page">
        <p className="intro">{intro}</p>
        <TagFilter tags={tags} activeTag={tag} onSelect={(name) => setParam("tag", name)} />
        <BrowseControls query={query} view={view} sort={sort} defaultSort={defaultSort} onChange={setParam} />
        {shown?.length === 0 && <p className="quiet">{query ? "Nothing matches that." : "Nothing here yet."}</p>}
        {shown && view === "rows" && <EntryRows entries={shown} activeTag={tag} />}
        {shown && view !== "rows" && <EntryGrid entries={shown} activeTag={tag} size={view} />}
      </main>
      <SiteFooter />
    </>
  );
}
