/**
 * BrowsePanel: every way to move around a board, above the work, in the
 * shape every page shares (components/SectionLine + ControlBand):
 *
 *   spaces  the boards, as larger words; the one you're in is in accent.
 *           Each is its own page, so spaces never mix. Switching keeps the
 *           view and drops what you'd picked.
 *   view    search, sphere / three picture sizes / rows, sort, clear; then
 *           a caret that opens
 *   tags    the board's tags, a list in aligned columns; pick one to
 *           highlight it
 *   time    a slider over the months that have entries
 *
 * While tags and time are closed, a picked tag or span still shows beside
 * the caret (PickedFilters). Used by BoardPage, which loads the boards, tags
 * and entries it shows. Every pick lives in the URL (useBrowseParams).
 */

import { useMemo } from "react";
import { ControlBand } from "../../components/ControlBand";
import { PageRow } from "../../components/PageRow";
import { SectionLine } from "../../components/SectionLine";
import type { Board, Entry, Tag } from "../../types/entry";
import { boardPath } from "./boardPath";
import { BrowseControls } from "./BrowseControls";
import { countMonths } from "./monthRange";
import { PickedFilters } from "./PickedFilters";
import { TagFilter } from "./TagFilter";
import { TimeRangeFilter } from "./TimeRangeFilter";
import { DEFAULT_VIEW, type useBrowseParams } from "./useBrowseParams";

interface Props {
  boards: Board[];
  board: string;
  tags: Tag[];
  /** The whole board (not a search's results), so the time slider always spans all of it. */
  entries: Entry[];
  browse: ReturnType<typeof useBrowseParams>;
}

export function BrowsePanel({ boards, board, tags, entries, browse }: Props) {
  const months = useMemo(() => countMonths(entries), [entries]);
  const keepView = browse.view === DEFAULT_VIEW ? "" : `?view=${browse.view}`;
  const sections = boards.map((candidate) => ({
    key: candidate.slug,
    label: candidate.name.toLowerCase(),
    to: `${boardPath(candidate.slug)}${keepView}`,
  }));

  return (
    <section className="browse-panel">
      <SectionLine label="Spaces" sections={sections} current={board} />
      <ControlBand
        rememberAs="board-filters-open"
        controls={
          <BrowseControls
            query={browse.query}
            view={browse.view}
            sort={browse.sort}
            defaultSort={browse.defaultSort}
            hasFilters={browse.hasFilters}
            onChange={browse.setParam}
            onClear={browse.clearFilters}
          />
        }
        picked={
          <PickedFilters
            tag={browse.tag}
            range={browse.range}
            onClearTag={() => browse.setParam("tag", null)}
            onClearRange={() => browse.setRange(null)}
          />
        }
        more={
          <>
            <PageRow>
              <TagFilter tags={tags} activeTag={browse.tag} onSelect={(name) => browse.setParam("tag", name)} />
            </PageRow>
            <PageRow>
              <TimeRangeFilter months={months} range={browse.range} onChange={browse.setRange} />
            </PageRow>
          </>
        }
      />
    </section>
  );
}
