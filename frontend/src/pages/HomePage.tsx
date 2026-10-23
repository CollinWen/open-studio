/**
 * HomePage ( / ): the home board (the owner's own collection), laid out as labeled rows. The intro
 * set large, the tags, the years, the browse controls (search, view, sort),
 * then the entries: on an orb by default, or as a grid or rows. A picked tag
 * or years highlight their entries in whichever view is showing, and every
 * active filter is listed as a pill beside the browse controls, ready to clear.
 *
 * Entries load a page at a time (useEntryPages): the first pictures show at
 * once and the rest rise in behind them, with "loading" breathing in the
 * header until the last page is in. After the owner saves an entry the
 * page reloads quietly.
 *
 * Every choice lives in the URL (see useBrowseParams), so any view can be
 * shared or linked to. Selecting a tag swaps the intro for that tag's
 * description.
 */

import { useEffect, useMemo, useState } from "react";
import { searchEntries } from "../api/searchApi";
import { fetchTags } from "../api/tagsApi";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { ActiveFilters } from "../features/grid/ActiveFilters";
import { BrowseControls } from "../features/grid/BrowseControls";
import { EntryGrid } from "../features/grid/EntryGrid";
import { EntryRows } from "../features/grid/EntryRows";
import { SphereView } from "../features/grid/SphereView";
import { sortEntries } from "../features/grid/sortEntries";
import { TagFilter } from "../features/grid/TagFilter";
import { YearFilter } from "../features/grid/YearFilter";
import { yearOf } from "../features/grid/entryHighlight";
import { useBrowseParams } from "../features/grid/useBrowseParams";
import { useEntryPages } from "../features/grid/useEntryPages";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import type { Entry, Tag } from "../types/entry";

const INTRO = "A working collection of things I make and things I'm curious about.";
// The home page shows the owner's own board; other boards are separate spaces.
const HOME_BOARD = "home";

export function HomePage() {
  const { tag, pickedYears, query, view, sort, defaultSort, setParam, toggleYear, clearParams } = useBrowseParams();
  const collection = useEntryPages(HOME_BOARD, !query);
  const [found, setFound] = useState<Entry[] | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const entries = query ? found : collection.entries;

  // Once every page is in, so the counts match what's shown (and again after a save).
  useEffect(() => {
    if (!collection.loading) fetchTags(HOME_BOARD).then(setTags).catch(console.error);
  }, [collection.loading]);

  useEffect(() => {
    setFound(null);
    if (query) searchEntries(query, HOME_BOARD).then(setFound).catch(() => setFound([]));
  }, [query]);
  useOnEntrySaved(collection.reload);

  const activeTag = tags.find((candidate) => candidate.name === tag);
  const intro = tag ? activeTag?.description || `Everything tagged “${tag}”.` : INTRO;
  // Kept stable between renders so the sphere doesn't rebuild on every hover.
  const shown = useMemo(() => entries && sortEntries(entries, sort), [entries, sort]);

  // Picked years stay listed even when a search leaves no entries from them, so they can be seen and cleared.
  const years = useMemo(
    () => [...new Set([...(entries?.map(yearOf) ?? []), ...pickedYears])].sort().reverse(),
    [entries, pickedYears],
  );
  const highlight = useMemo(() => ({ tag, years: pickedYears }), [tag, pickedYears]);

  return (
    <>
      <SiteHeader>
        {entries && `${entries.length} ${entries.length === 1 ? "entry" : "entries"}`}
        {!query && collection.loading && <span className="loading-word">loading</span>}
      </SiteHeader>
      <main>
        <LabelRow rule="double" label={tag ? "Tag" : "Open Studio"} className="intro-row">
          <p className="display">{intro}</p>
        </LabelRow>
        <LabelRow rule="single" label="Tags">
          <TagFilter tags={tags} activeTag={tag} onSelect={(name) => setParam("tag", name)} />
        </LabelRow>
        <LabelRow rule="single" label="Years">
          <YearFilter years={years} pickedYears={pickedYears} onToggle={toggleYear} />
        </LabelRow>
        <LabelRow
          rule="single"
          label={
            <ActiveFilters
              tag={tag}
              pickedYears={pickedYears}
              query={query}
              onToggleYear={toggleYear}
              onClear={clearParams}
            />
          }
        >
          <BrowseControls query={query} view={view} sort={sort} defaultSort={defaultSort} onChange={setParam} />
        </LabelRow>
        <LabelRow wide>
          {shown?.length === 0 && <p className="quiet">{query ? "Nothing matches that." : "Nothing here yet."}</p>}
          {shown && view === "sphere" && shown.length > 0 && <SphereView entries={shown} highlight={highlight} />}
          {shown && view === "rows" && (
            <EntryRows entries={shown} highlight={highlight} arriveOrder={collection.orderOf} />
          )}
          {shown && view !== "rows" && view !== "sphere" && (
            <EntryGrid entries={shown} highlight={highlight} size={view} arriveOrder={collection.orderOf} />
          )}
        </LabelRow>
      </main>
      <SiteFooter />
    </>
  );
}
