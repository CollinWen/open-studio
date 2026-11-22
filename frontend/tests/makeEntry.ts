/**
 * makeEntry: a plain entry for tests, with any fields given replacing the
 * defaults. Used by the tests under tests/features/.
 */

import type { Entry } from "../src/types/entry";

export function makeEntry(fields: Partial<Entry> = {}): Entry {
  return {
    id: "e1",
    title: "An entry",
    description: "",
    kind: "note",
    source_name: "",
    source_url: "",
    media: [],
    occurred_at: "2024-03-10T00:00:00",
    created_at: "2024-03-10T00:00:00",
    updated_at: "2024-03-10T00:00:00",
    visibility: "public",
    tags: [],
    added_by: "owner",
    board: "home",
    pinned: false,
    ...fields,
  };
}
