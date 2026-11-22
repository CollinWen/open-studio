/**
 * Tests for describeRunState: running, finished and run-out runs each read
 * in plain words with how long ago.
 */

import { describe, expect, it } from "vitest";
import { describeRunState } from "../../../src/features/studio/describeRunState";
import type { Run } from "../../../src/types/run";

const NOW = Date.parse("2026-11-20T12:00:00Z");

function makeRun(fields: Partial<Run>): Run {
  return {
    id: "r1",
    agent: "scout",
    kind: "study",
    board: "bread",
    brief: "",
    entry_id: null,
    tools: [],
    started_by: "owner",
    created_at: "2026-11-20T10:00:00",
    expires_at: "2026-11-20T14:00:00",
    finished_at: null,
    session_url: "",
    summary: "",
    state: "running",
    scopes: [],
    added: [],
    ...fields,
  };
}

describe("describeRunState", () => {
  it("says how long a running run has been going", () => {
    expect(describeRunState(makeRun({}), NOW)).toBe("running, started 2 h ago");
  });

  it("says when a run finished", () => {
    const finished = makeRun({ state: "finished", finished_at: "2026-11-20T11:55:00" });
    expect(describeRunState(finished, NOW)).toBe("finished 5 min ago");
  });

  it("says when a run ran out", () => {
    const expired = makeRun({ state: "expired", expires_at: "2026-11-20T11:00:00" });
    expect(describeRunState(expired, NOW)).toBe("ran out 1 h ago");
  });
});
