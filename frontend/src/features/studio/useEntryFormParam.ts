/**
 * useEntryFormParam: whether the entry form is open, read from the URL.
 * `?add` opens it blank and `?edit=<id>` opens that entry, on any page, so
 * the form opens over whatever you're looking at and can be linked to.
 *
 * Used by EntryFormModal (which shows it) and by every "add" and "edit" word.
 */

import { useSearchParams } from "react-router-dom";

export function useEntryFormParam() {
  const [params, setParams] = useSearchParams();

  const change = (update: (next: URLSearchParams) => void) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        next.delete("add");
        next.delete("edit");
        update(next);
        return next;
      },
      { replace: false },
    );

  return {
    isAdding: params.has("add"),
    editId: params.get("edit"),
    openNewEntry: () => change((next) => next.set("add", "")),
    openEntryEdit: (id: string) => change((next) => next.set("edit", id)),
    closeEntryForm: () => change(() => {}),
  };
}
