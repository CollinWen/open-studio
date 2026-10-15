/**
 * SketchPage ( /sketch ): a scratch page for trying home-page ideas on the
 * real collection before any of them goes on the home page. Not linked from
 * anywhere. Right now: a tight contact sheet with threads between related
 * entries, in three styles, at three sizes and three gaps.
 *
 *   ?sketch=hover | threads | kinship   (default hover)
 *   ?size=small | medium | large        (default medium)
 *   ?gap=none | hairline | narrow       (default hairline)
 *
 * The sketches live in features/sketches/. Delete this page and that folder
 * once an idea graduates to the home page.
 */

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchEntries } from "../api/entriesApi";
import { SiteHeader } from "../components/SiteHeader";
import { WordChoice } from "../components/WordChoice";
import { ContactSheet, type ThreadStyle } from "../features/sketches/ContactSheet";
import { fetchRelatedMap, listLinks, orderByKinship, type RelatedMap } from "../features/sketches/relatedLinks";
import type { Entry } from "../types/entry";

const SKETCHES: ThreadStyle[] = ["hover", "threads", "kinship"];
const ROW_HEIGHTS = { small: 120, medium: 200, large: 320 };
const GAPS = { none: 0, hairline: 3, narrow: 10 };

export function SketchPage() {
  const [params, setParams] = useSearchParams();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [related, setRelated] = useState<RelatedMap>(new Map());

  const sketch = pick(params.get("sketch"), SKETCHES, "hover");
  const size = pick(params.get("size"), Object.keys(ROW_HEIGHTS) as (keyof typeof ROW_HEIGHTS)[], "medium");
  const gap = pick(params.get("gap"), Object.keys(GAPS) as (keyof typeof GAPS)[], "hairline");

  useEffect(() => {
    fetchEntries()
      .then((loaded) => {
        setEntries(loaded);
        return fetchRelatedMap(loaded);
      })
      .then(setRelated)
      .catch(console.error);
  }, []);

  const links = useMemo(() => listLinks(related), [related]);
  const ordered = useMemo(
    () =>
      sketch === "kinship"
        ? orderByKinship(entries, related)
        : [...entries].sort((a, b) => b.occurred_at.localeCompare(a.occurred_at)),
    [entries, related, sketch],
  );

  const choose = (name: string, value: string) =>
    setParams((current) => {
      const next = new URLSearchParams(current);
      next.set(name, value);
      return next;
    });

  return (
    <>
      <SiteHeader>sketch</SiteHeader>
      <div className="sketch-controls">
        <Choices options={SKETCHES} current={sketch} onPick={(value) => choose("sketch", value)} />
        <Choices options={Object.keys(ROW_HEIGHTS)} current={size} onPick={(value) => choose("size", value)} />
        <Choices options={Object.keys(GAPS)} current={gap} onPick={(value) => choose("gap", value)} />
      </div>
      <ContactSheet
        entries={ordered}
        links={links}
        threadStyle={sketch}
        rowHeight={ROW_HEIGHTS[size]}
        gap={GAPS[gap]}
      />
    </>
  );
}

function Choices({
  options,
  current,
  onPick,
}: {
  options: string[];
  current: string;
  onPick: (value: string) => void;
}) {
  return (
    <span className="word-list">
      {options.map((option) => (
        <WordChoice key={option} label={option} active={option === current} onPick={() => onPick(option)} />
      ))}
    </span>
  );
}

function pick<T extends string>(value: string | null, options: readonly T[], fallback: T): T {
  return options.includes(value as T) ? (value as T) : fallback;
}
