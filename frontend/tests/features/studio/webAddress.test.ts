/**
 * Tests for webAddress: a bare address gets https://, spaces are trimmed,
 * and anything else (a scheme, a word) is left for the backend to refuse.
 */

import { describe, expect, it } from "vitest";
import { toWebAddress } from "../../../src/features/studio/webAddress";

describe("toWebAddress", () => {
  it("adds https:// to a bare address", () => {
    expect(toWebAddress("example.com/recipe")).toBe("https://example.com/recipe");
    expect(toWebAddress("www.youtube.com/watch?v=abc")).toBe("https://www.youtube.com/watch?v=abc");
  });

  it("trims spaces and keeps a full address as it is", () => {
    expect(toWebAddress("  https://example.com  ")).toBe("https://example.com");
  });

  it("leaves other schemes and plain words alone", () => {
    expect(toWebAddress("javascript:alert(1)")).toBe("javascript:alert(1)");
    expect(toWebAddress("mailto:a@b.co")).toBe("mailto:a@b.co");
    expect(toWebAddress("bread")).toBe("bread");
    expect(toWebAddress("two words.com")).toBe("two words.com");
  });
});
