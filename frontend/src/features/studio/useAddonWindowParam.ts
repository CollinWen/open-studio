/**
 * useAddonWindowParam: which of the studio's add-on windows is open, read
 * from the URL, so each can be linked to: `?add-addon` (define one) and
 * `?addon=<name>` (its guide, and for a Composio add-on its tools).
 * Opening and closing replaces the address instead of adding to the history.
 *
 * Used by AddonManager.
 */

import { useSearchParams } from "react-router-dom";

export function useAddonWindowParam() {
  const [params, setParams] = useSearchParams();

  const change = (update: (next: URLSearchParams) => void) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        next.delete("add-addon");
        next.delete("addon");
        update(next);
        return next;
      },
      { replace: true },
    );

  return {
    isAddingAddon: params.has("add-addon"),
    openAddon: params.get("addon"),
    openNewAddon: () => change((next) => next.set("add-addon", "")),
    openAddonGuide: (name: string) => change((next) => next.set("addon", name)),
    closeAddonWindows: () => change(() => {}),
  };
}
