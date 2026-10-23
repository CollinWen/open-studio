/**
 * useBrowseParams: everything about how a board is being browsed, kept in
 * the URL so any view is a link you can share or come back to:
 *
 *   ?tag=fermentation           highlight one tag
 *   ?from=2023-04&to=2024-09    highlight a span of months (and turn the sphere to it)
 *   ?q=bread                    search
 *   ?view=rows                  sphere | small | medium | large | rows   (default sphere)
 *   ?sort=oldest                recent | oldest | title | relevance (default: relevance when searching, else recent)
 *
 * Which board is showing is the page's address itself ("/", "/b/bread").
 * Default values are left out of the URL to keep links clean.
 */

import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import type { MonthRange } from "./monthRange";

export const VIEWS = ["sphere", "small", "medium", "large", "rows"] as const;
export type View = (typeof VIEWS)[number];
export const DEFAULT_VIEW: View = "sphere";

export const SORTS = ["recent", "oldest", "title", "relevance"] as const;
export type Sort = (typeof SORTS)[number];

export type Param = "tag" | "from" | "to" | "q" | "view" | "sort";
/** Everything that narrows what's highlighted or shown; "clear" removes all of these. */
export const FILTER_PARAMS: Param[] = ["tag", "from", "to", "q"];

const MONTH = /^\d{4}-\d{2}$/;

export function useBrowseParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const tag = searchParams.get("tag");
  const from = searchParams.get("from") ?? "";
  const to = searchParams.get("to") ?? "";
  // The same object until the URL changes, so views keyed on it don't redo work on every render.
  const range = useMemo<MonthRange | null>(
    () => (MONTH.test(from) && MONTH.test(to) && from <= to ? { from, to } : null),
    [from, to],
  );
  const query = searchParams.get("q") ?? "";
  const view = asOneOf(searchParams.get("view"), VIEWS, DEFAULT_VIEW);
  const defaultSort: Sort = query ? "relevance" : "recent";
  const sort = asOneOf(searchParams.get("sort"), SORTS, defaultSort);

  /** Set some values at once (null removes one). Typing and dragging replace history instead of adding to it. */
  const setParams = (values: Partial<Record<Param, string | null>>) => {
    setSearchParams(
      (current) => {
        const next = new URLSearchParams(current);
        for (const [name, value] of Object.entries(values)) {
          if (value) next.set(name, value);
          else next.delete(name);
        }
        return next;
      },
      { replace: "q" in values || "from" in values },
    );
  };

  const setParam = (name: Param, value: string | null) => setParams({ [name]: value });
  const setRange = (picked: MonthRange | null) => setParams({ from: picked?.from ?? null, to: picked?.to ?? null });
  const clearFilters = () => setParams(Object.fromEntries(FILTER_PARAMS.map((name) => [name, null])));
  const hasFilters = Boolean(tag || range || query);

  return { tag, range, query, view, sort, defaultSort, hasFilters, setParam, setRange, clearFilters };
}

function asOneOf<T extends string>(value: string | null, options: readonly T[], fallback: T): T {
  return options.includes(value as T) ? (value as T) : fallback;
}
