/**
 * BoardPage ( / and /b/:board ): one board, the space you're in. "/" is the
 * home board (the owner's own collection); every other board has its own
 * address and shows only its own entries, tags and time, so spaces never mix.
 *
 * Laid out as labeled rows: first the browse panel (boards, view, tags,
 * time: every way to move around, in one block), then the work, as medium
 * pictures by default, or small or large ones, or rows. There is no intro
 * above: the board's brief (its description, or a picked tag's) is the
 * first tile of the work (BoardBrief), beside the pinned entries. A picked
 * tag or span of months highlights its entries in whichever view is showing.
 *
 * Entries load a page at a time (useEntryPages): the first page fades in
 * whole and the rest rise in behind it. Only a few screens of them are
 * drawn at first, more as the visitor scrolls (useShownCount). Switching
 * boards fades the one on screen out until the next board's first page is
 * in, then fades that in, so nothing empties and refills. Until a board's
 * first page is in (or a search's results), the large studio mark sweeps
 * where the view will be; the board's count appears beside its name once
 * the last page is in.
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
import { HOME_BOARD } from "../features/grid/boardPath";
import { BoardBrief } from "../features/grid/BoardBrief";
import { BrowsePanel } from "../features/grid/BrowsePanel";
import { EntryGrid } from "../features/grid/EntryGrid";
import { EntryRows } from "../features/grid/EntryRows";
import { sortEntries } from "../features/grid/sortEntries";
import { useBrowseParams } from "../features/grid/useBrowseParams";
import { useEntryPages } from "../features/grid/useEntryPages";
import { useShownCount } from "../features/grid/useShownCount";
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
  const boardBrief = board === HOME_BOARD ? HOME_INTRO : current?.description || current?.name || "";
  const brief = tag ? (
    <BoardBrief label={`tagged “${tag}”`} text={activeTag?.description || `Everything tagged “${tag}” stands out.`} />
  ) : (
    boardBrief && <BoardBrief label="about this board" text={boardBrief} />
  );
  // Kept stable between renders so the views don't redo work on every hover.
  const shown = useMemo(() => entries && sortEntries(entries, sort), [entries, sort]);
  const highlight = useMemo(() => ({ tag, range }), [tag, range]);
  const { shownCount, markerRef } = useShownCount(shown?.length ?? 0, `${board} ${query} ${sort}`);
  const drawn = useMemo(() => shown?.slice(0, shownCount), [shown, shownCount]);

  if (boards && !current) return <NotFoundPage />;

  return (
    <>
      <main>
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
          // While another board loads, the one on screen fades out; the new one fades in whole.
          <LabelRow wide className={collection.switching ? "is-leaving" : undefined}>
            {!shown && <LoadingMark />}
            <div key={collection.entriesBoard ?? ""} className="board-work">
              {drawn && view === "rows" && (
                <>
                  {brief}
                  <EntryRows entries={drawn} highlight={highlight} arriveOrder={collection.orderOf} />
                </>
              )}
              {drawn && view !== "rows" && (
                <EntryGrid entries={drawn} highlight={highlight} size={view} arriveOrder={collection.orderOf} lead={brief} />
              )}
            </div>
            <div ref={markerRef} aria-hidden="true" />
          </LabelRow>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
