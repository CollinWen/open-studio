/**
 * Tests for linkSite: the site shown beside a session link is the link's
 * real host, so a look-alike address can't pass for claude.ai.
 */

import { describe, expect, it } from "vitest";
import { linkSite } from "../../../src/features/studio/linkSite";

describe("linkSite", () => {
  it("gives the host of a web address", () => {
    expect(linkSite("https://claude.ai/code/session_abc")).toBe("claude.ai");
  });

  it("shows the real host of a look-alike", () => {
    expect(linkSite("https://claude.ai.example.com/session")).toBe("claude.ai.example.com");
    expect(linkSite("https://example.com/claude.ai")).toBe("example.com");
    expect(linkSite("https://claude.ai@example.com/")).toBe("example.com");
  });

  it("gives back anything that isn't a full address as it is", () => {
    expect(linkSite("not a link")).toBe("not a link");
  });
});
