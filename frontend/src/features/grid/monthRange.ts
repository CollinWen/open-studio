/**
 * monthRange: months as the time slider sees them. An entry's month
 * ("2024-03"), every month from a board's first entry to its last (with how
 * many entries each has, gaps included so the slider runs evenly), how a
 * month reads ("Mar 2024"), and whether one falls inside a picked range.
 *
 * Used by TimeRangeFilter, entryHighlight and BoardPage.
 */

import type { Entry } from "../../types/entry";

/** A picked span of months, both ends included ("2023-04" to "2024-09"). */
export interface MonthRange {
  from: string;
  to: string;
}

export interface MonthCount {
  month: string;
  count: number;
}

export function monthOf(entry: Entry): string {
  return entry.occurred_at.slice(0, 7);
}

/** Every month from the earliest entry to the latest, oldest first, each with its entry count. */
export function countMonths(entries: Entry[]): MonthCount[] {
  if (entries.length === 0) return [];
  const counts = new Map<string, number>();
  for (const entry of entries) counts.set(monthOf(entry), (counts.get(monthOf(entry)) ?? 0) + 1);
  const sorted = [...counts.keys()].sort();
  const months: MonthCount[] = [];
  for (let month = sorted[0]; month <= sorted[sorted.length - 1]; month = nextMonth(month)) {
    months.push({ month, count: counts.get(month) ?? 0 });
  }
  return months;
}

export function isInRange(month: string, range: MonthRange): boolean {
  return month >= range.from && month <= range.to;
}

const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function formatMonth(month: string): string {
  return `${MONTH_NAMES[Number(month.slice(5, 7)) - 1]} ${month.slice(0, 4)}`;
}

function nextMonth(month: string): string {
  const year = Number(month.slice(0, 4));
  const index = Number(month.slice(5, 7));
  return index === 12 ? `${year + 1}-01` : `${year}-${String(index + 1).padStart(2, "0")}`;
}
