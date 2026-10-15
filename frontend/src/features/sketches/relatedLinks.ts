/**
 * relatedLinks: the connections drawn in the sketches. Asks the backend for
 * each entry's related entries (closest in meaning) and keeps the strongest
 * few as links. Also orders entries "by kinship": a walk that always steps
 * to the closest unvisited relative, so related work ends up side by side.
 *
 * Used by SketchPage. Each entry's relatives come back ranked, closest first.
 */

import { fetchRelatedEntries } from "../../api/entriesApi";
import type { Entry } from "../../types/entry";

/** Entry id → ids of its closest relatives, closest first. */
export type RelatedMap = Map<string, string[]>;

export interface Link {
  from: string;
  to: string;
  /** 0 for an entry's closest relative, 1 for the next, and so on. */
  rank: number;
}

/** How many relatives per entry become drawn links. */
const LINKS_PER_ENTRY = 3;

export async function fetchRelatedMap(entries: Entry[]): Promise<RelatedMap> {
  const shown = new Set(entries.map((entry) => entry.id));
  const lists = await Promise.all(entries.map((entry) => fetchRelatedEntries(entry.id).catch(() => [])));
  return new Map(entries.map((entry, i) => [entry.id, lists[i].map((related) => related.id).filter((id) => shown.has(id))]));
}

/** Each pair once, keeping its stronger rank. */
export function listLinks(related: RelatedMap): Link[] {
  const byPair = new Map<string, Link>();
  for (const [from, relatives] of related) {
    relatives.slice(0, LINKS_PER_ENTRY).forEach((to, rank) => {
      const key = [from, to].sort().join("|");
      const existing = byPair.get(key);
      if (!existing || rank < existing.rank) byPair.set(key, { from, to, rank });
    });
  }
  return [...byPair.values()];
}

/** Newest first, but each step goes to the closest unvisited relative when there is one. */
export function orderByKinship(entries: Entry[], related: RelatedMap): Entry[] {
  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  const newestFirst = [...entries].sort((a, b) => b.occurred_at.localeCompare(a.occurred_at));
  const visited = new Set<string>();
  const order: Entry[] = [];
  let current: Entry | undefined = newestFirst[0];
  while (current) {
    visited.add(current.id);
    order.push(current);
    const nextId: string | undefined = (related.get(current.id) ?? []).find((id) => !visited.has(id));
    current = nextId ? byId.get(nextId) : newestFirst.find((entry) => !visited.has(entry.id));
  }
  return order;
}
