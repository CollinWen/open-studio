/**
 * useAgentWindowParam: which of the studio's agent windows is open, read
 * from the URL, so each can be linked to: `?add-agent`, `?agent=<name>`
 * (change one) and `?issue=<name>` (issue it a token).
 * Opening and closing replaces the address instead of adding to the history.
 * A token, once issued, is never put in the URL.
 *
 * Used by AgentManager.
 */

import { useSearchParams } from "react-router-dom";

export function useAgentWindowParam() {
  const [params, setParams] = useSearchParams();

  const change = (update: (next: URLSearchParams) => void) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        next.delete("add-agent");
        next.delete("agent");
        next.delete("issue");
        update(next);
        return next;
      },
      { replace: true },
    );

  return {
    isAddingAgent: params.has("add-agent"),
    editingAgent: params.get("agent"),
    issuingFor: params.get("issue"),
    openNewAgent: () => change((next) => next.set("add-agent", "")),
    openAgentEdit: (name: string) => change((next) => next.set("agent", name)),
    openTokenIssue: (name: string) => change((next) => next.set("issue", name)),
    closeAgentWindows: () => change(() => {}),
  };
}
