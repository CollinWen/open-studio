/**
 * useBrowseParams: everything about how the home page is being browsed,
 * kept in the URL so any view is a link you can share or come back to:
 *
 *   ?tag=fermentation   highlight one tag
 *   ?q=bread            search
 *   ?view=rows          small | medium | large | rows   (default medium)
 *   ?sort=oldest        recent | oldest | title | relevance (default: relevance when searching, else recent)
 *
 * Default values are left out of the URL to keep links clean.
 */

import { useSearchParams } from "react-router-dom";

export const VIEWS = ["small", "medium", "large", "rows"] as const;
export type View = (typeof VIEWS)[number];

export const SORTS = ["recent", "oldest", "title", "relevance"] as const;
export type Sort = (typeof SORTS)[number];

type Param = "tag" | "q" | "view" | "sort";

export function useBrowseParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const tag = searchParams.get("tag");
  const query = searchParams.get("q") ?? "";
  const view = asOneOf(searchParams.get("view"), VIEWS, "medium");
  const defaultSort: Sort = query ? "relevance" : "recent";
  const sort = asOneOf(searchParams.get("sort"), SORTS, defaultSort);

  /** Set one value (null removes it). Typing in search replaces history instead of adding to it. */
  const setParam = (name: Param, value: string | null) => {
    setSearchParams(
      (current) => {
        const next = new URLSearchParams(current);
        if (value) next.set(name, value);
        else next.delete(name);
        return next;
      },
      { replace: name === "q" },
    );
  };

  return { tag, query, view, sort, defaultSort, setParam };
}

function asOneOf<T extends string>(value: string | null, options: readonly T[], fallback: T): T {
  return options.includes(value as T) ? (value as T) : fallback;
}
