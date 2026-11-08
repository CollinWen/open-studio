/**
 * BoardPage ( / and /b/:board ): one board, the space you're in. "/" is the
 * home board (the owner's own collection); every other board has its own
 * address and shows only its own entries, tags and time, so spaces never mix.
 *
 * Laid out as labeled rows: the intro set large (the board's description,
 * or a picked tag's) in a block of fixed height, so a longer or shorter
 * intro never moves what's below it; then the browse panel (boards, view,
 * tags, time: every way to move around, in one block), then the entries as
 * a grid of medium pictures by default, or small, large or rows. A picked
 * tag or span of months highlights its entries in whichever view is showing.
 *
 * Entries load a page at a time (useEntryPages): the first pictures show at
 * once and the rest rise in behind them. Until the first page is in (or a
 * search's results), the large studio mark sweeps where the view will be;
 * the board's count appears beside its name once the last page is in.
 * After the owner saves an entry the page reloads quietly. Every choice
 * lives in the URL (useBrowseParams). An address for a board that doesn't
 * exist (/b/nope) shows the not-found page instead of an empty board.
 */

import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchBoards } from "../api/boardsApi";
import { searchEntries } from "../api/searchApi";
import { fetchTags } from "../api/tagsApi";
import { LabelRow } from "../components/LabelRow";
import { LoadingMark } from "../components/LoadingMark";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";
import { HOME_BOARD } from "../features/grid/boardPath";
import { BrowsePanel } from "../features/grid/BrowsePanel";
import { EntryGrid } from "../features/grid/EntryGrid";
import { EntryRows } from "../features/grid/EntryRows";
import { sortEntries } from "../features/grid/sortEntries";
import { useBrowseParams } from "../features/grid/useBrowseParams";
import { useEntryPages } from "../features/grid/useEntryPages";
import { useOnEntrySaved } from "../features/studio/entrySavedEvent";
import { NotFoundPage } from "./NotFoundPage";
import type { Board, Entry, Tag } from "../types/entry";

const HOME_INTRO = "A working collection of things I make and things I'm curious about.";

export function BoardPage() {
  const { board = HOME_BOARD } = useParams();
  const browse = useBrowseParams();
  const { tag, range, query, view, sort } = browse;
  const collection = useEntryPages(board);
  // Null until the list arrives, so a board isn't called missing before we know.
  const [boards, setBoards] = useState<Board[] | null>(null);
  const [found, setFound] = useState<Entry[] | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const entries = query ? found : collection.entries;

  useEffect(() => {
    fetchBoards().then(setBoards).catch(console.error);
  }, []);

  // Once every page is in, so the counts match what's shown (and again after a save).
  useEffect(() => {
    if (!collection.loading) fetchTags(board).then(setTags).catch(console.error);
  }, [board, collection.loading]);

  useEffect(() => {
    setFound(null);
    if (query) searchEntries(query, board).then(setFound).catch(() => setFound([]));
  }, [query, board]);
  useOnEntrySaved(collection.reload);

  const current = boards?.find((candidate) => candidate.slug === board);
  const activeTag = tags.find((candidate) => candidate.name === tag);
  const boardIntro = board === HOME_BOARD ? HOME_INTRO : current?.description || current?.name;
  const intro = tag ? activeTag?.description || `Everything tagged “${tag}”.` : boardIntro;
  // Kept stable between renders so the views don't redo work on every hover.
  const shown = useMemo(() => entries && sortEntries(entries, sort), [entries, sort]);
  const highlight = useMemo(() => ({ tag, range }), [tag, range]);

  if (boards && !current) return <NotFoundPage />;

  return (
    <>
      <SiteHeader />
      <main>
        <LabelRow rule="double" className="intro-row board-intro">
          <p className="display">{intro}</p>
        </LabelRow>
        <BrowsePanel
          boards={boards ?? []}
          board={board}
          tags={tags}
          entries={collection.entries ?? []}
          count={collection.loading ? undefined : collection.entries?.length}
          browse={browse}
        />
        {shown?.length === 0 ? (
          // A plain row, so the message starts on the left edge like other text, and no view draws an empty list.
          <LabelRow>
            <p className="quiet">{query ? "Nothing matches that." : "Nothing here yet."}</p>
          </LabelRow>
        ) : (
          <LabelRow wide>
            {!shown && <LoadingMark />}
            {shown && view === "rows" && (
              <EntryRows entries={shown} highlight={highlight} arriveOrder={collection.orderOf} />
            )}
            {shown && view !== "rows" && (
              <EntryGrid entries={shown} highlight={highlight} size={view} arriveOrder={collection.orderOf} />
            )}
          </LabelRow>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
