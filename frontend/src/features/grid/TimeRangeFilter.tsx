/**
 * TimeRangeFilter: the board's time, as a slider. The picked span in words
 * ("Mar 2021 – Sep 2024", or "all time"), then a strip of thin bars, one
 * per month from the first entry to the last, each as tall as that month is
 * full; two handles pick a span of months. Entries inside it stand out in
 * every view and the sphere turns to face them; the bars outside it fade.
 * Years are marked underneath; "show all time" lets go of the span. While
 * a handle moves, its place is kept here (the URL catches up a moment later).
 *
 * Used by BrowsePanel. Months come from monthRange.ts; the span lives in the
 * URL (?from=&to=, see useBrowseParams). Looks: .time-filter in global.css.
 */

import { useEffect, useState, type CSSProperties } from "react";
import { formatMonth, isInRange, type MonthCount, type MonthRange } from "./monthRange";

interface Props {
  months: MonthCount[];
  range: MonthRange | null;
  onChange: (range: MonthRange | null) => void;
}

export function TimeRangeFilter({ months, range, onChange }: Props) {
  const last = months.length - 1;
  const fromURL = range ? Math.max(0, months.findIndex((m) => m.month >= range.from)) : 0;
  const toURL = range ? lastIndexAtOrBefore(months, range.to) : last;
  const [held, setIndices] = useState([fromURL, toURL]);
  // Months can change under a held place (more pages loading), so keep it inside them.
  const [fromIndex, toIndex] = held.map((index) => Math.min(Math.max(index, 0), Math.max(last, 0)));

  // Follow the URL when it changes from outside (back button, a shared link, "clear").
  useEffect(() => setIndices([fromURL, toURL]), [fromURL, toURL]);

  if (months.length < 2) return null;
  const fullest = Math.max(...months.map((m) => m.count));
  const shown = { from: months[fromIndex].month, to: months[toIndex].month };
  const isAllTime = fromIndex === 0 && toIndex === last;

  /** Keep the handles from crossing; picking everything again means no filter at all. */
  const pick = (from: number, to: number) => {
    const [low, high] = from <= to ? [from, to] : [to, from];
    setIndices([low, high]);
    onChange(low === 0 && high === last ? null : { from: months[low].month, to: months[high].month });
  };
  const at = (index: number) => ({ "--at": index / last }) as CSSProperties;

  return (
    <div className="time-filter">
      <p className="word-list">
        <span>{isAllTime ? "all time" : `${formatMonth(shown.from)} – ${formatMonth(shown.to)}`}</span>
        {!isAllTime && (
          <button type="button" className="quiet" onClick={() => pick(0, last)}>
            show all time
          </button>
        )}
      </p>
      <div className="time-strip">
        <div className="time-bars" aria-hidden="true">
          {months.map((m, index) =>
            m.count === 0 ? null : (
              <span
                key={m.month}
                className={isInRange(m.month, shown) ? "time-bar is-in" : "time-bar"}
                style={{ ...at(index), "--fill": m.count / fullest } as CSSProperties}
              />
            ),
          )}
        </div>
        <input
          type="range"
          min={0}
          max={last}
          value={fromIndex}
          aria-label="From"
          aria-valuetext={formatMonth(months[fromIndex].month)}
          onChange={(event) => pick(Number(event.target.value), toIndex)}
        />
        <input
          type="range"
          min={0}
          max={last}
          value={toIndex}
          aria-label="To"
          aria-valuetext={formatMonth(months[toIndex].month)}
          onChange={(event) => pick(fromIndex, Number(event.target.value))}
        />
      </div>
      <div className="time-years" aria-hidden="true">
        {months.map((m, index) =>
          m.month.endsWith("-01") || index === 0 ? (
            <span key={m.month} style={at(index)}>
              {m.month.slice(0, 4)}
            </span>
          ) : null,
        )}
      </div>
    </div>
  );
}

function lastIndexAtOrBefore(months: MonthCount[], month: string): number {
  for (let index = months.length - 1; index >= 0; index -= 1) if (months[index].month <= month) return index;
  return 0;
}
