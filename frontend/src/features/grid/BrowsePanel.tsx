/**
 * BrowsePanel: every way to move around a board, in two parts above the work.
 *
 *   Space   which board you're in (larger words, the current one in accent).
 *           Spaces are where you are, not a filter, so they stand on their own.
 *           Under them, the agents signed on to this board, if any.
 *
 *   Then, on a lightly shaded band (the controls, not the work):
 *   View    search, sphere / three picture sizes / rows, sort, clear
 *   Filter  "show tags & time" opens the two lines below; while they're
 *           closed, whatever you picked is still shown here (FilterSummary)
 *   Tags    the board's tags, each in an oval; pick one to highlight it
 *   Time    a slider over the months that have entries
 *
 * Whether tags & time are open is remembered in this browser only (it's how
 * you like the page, not what you're looking at, so it stays out of the URL).
 *
 * Used by BoardPage, which loads the boards, tags and entries it shows.
 * Every pick lives in the URL (useBrowseParams).
 */

import { useMemo, useState } from "react";
import { LabelRow } from "../../components/LabelRow";
import type { Board, Entry, Tag } from "../../types/entry";
import { BoardLine } from "./BoardLine";
import { BrowseControls } from "./BrowseControls";
import { FilterSummary } from "./FilterSummary";
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

const OPEN_KEY = "browse-filters-open";

export function BrowsePanel({ boards, board, tags, entries, browse }: Props) {
  const months = useMemo(() => countMonths(entries), [entries]);
  const [open, setOpen] = useState(readOpen);
  const agents = boards.find((candidate) => candidate.slug === board)?.agents ?? [];

  const toggle = () => {
    setOpen(!open);
    try {
      localStorage.setItem(OPEN_KEY, String(!open));
    } catch {
      // Storage can be blocked; the panel still works, it just won't remember.
    }
  };

  return (
    <section className="browse-panel">
      <LabelRow rule="single" label="Space" className="space-row">
        <BoardLine boards={boards} current={board} view={browse.view} />
        {agents.length > 0 && <p className="quiet board-agents">with {agents.join(", ")}</p>}
      </LabelRow>
      <div className="browse-controls-band">
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
        <LabelRow label="Filter">
          <FilterSummary
            open={open}
            onToggle={toggle}
            tag={browse.tag}
            range={browse.range}
            onClearTag={() => browse.setParam("tag", null)}
            onClearRange={() => browse.setRange(null)}
          />
        </LabelRow>
        {open && (
          <>
            <LabelRow label="Tags">
              <TagFilter tags={tags} activeTag={browse.tag} onSelect={(name) => browse.setParam("tag", name)} />
            </LabelRow>
            <LabelRow label="Time">
              <TimeRangeFilter months={months} range={browse.range} onChange={browse.setRange} />
            </LabelRow>
          </>
        )}
      </div>
    </section>
  );
}

function readOpen(): boolean {
  try {
    return localStorage.getItem(OPEN_KEY) === "true";
  } catch {
    return false;
  }
}
