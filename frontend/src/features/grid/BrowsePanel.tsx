/**
 * BrowsePanel: every way to move around a board, in one block above the
 * work, with no rules between its lines:
 *
 *   Space   which board you're in (larger words, the current one underlined)
 *   Tags    the board's tags, each in an oval; pick one to highlight it
 *   Time    a slider over the months that have entries
 *   View    search, sphere / three picture sizes / rows, sort, clear
 *
 * Used by BoardPage, which loads the boards, tags and entries it shows.
 * Every pick lives in the URL (useBrowseParams).
 */

import { useMemo } from "react";
import { LabelRow } from "../../components/LabelRow";
import type { Board, Entry, Tag } from "../../types/entry";
import { BoardLine } from "./BoardLine";
import { BrowseControls } from "./BrowseControls";
import { countMonths } from "./monthRange";
import { TagFilter } from "./TagFilter";
import { TimeRangeFilter } from "./TimeRangeFilter";
import type { useBrowseParams } from "./useBrowseParams";

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

  return (
    <section className="browse-panel">
      <LabelRow rule="single" label="Space">
        <BoardLine boards={boards} current={board} view={browse.view} />
      </LabelRow>
      <LabelRow label="Tags">
        <TagFilter tags={tags} activeTag={browse.tag} onSelect={(name) => browse.setParam("tag", name)} />
      </LabelRow>
      <LabelRow label="Time">
        <TimeRangeFilter months={months} range={browse.range} onChange={browse.setRange} />
      </LabelRow>
      <LabelRow label="View">
        <BrowseControls
          query={browse.query}
          view={browse.view}
          sort={browse.sort}
          defaultSort={browse.defaultSort}
          hasFilters={browse.hasFilters}
          onChange={browse.setParam}
          onClear={browse.clearFilters}
        />
      </LabelRow>
    </section>
  );
}
