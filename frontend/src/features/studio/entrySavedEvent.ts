/**
 * entrySavedEvent: tells whichever page is open that an entry was just
 * saved, so it can reload what it shows. The entry form opens over any page
 * and doesn't know what that page loaded.
 *
 * EntryFormModal announces; HomePage, EntryPage and StudioPage listen.
 */

import { useEffect } from "react";

const EVENT_NAME = "open-studio:entry-saved";

export function announceEntrySaved() {
  window.dispatchEvent(new Event(EVENT_NAME));
}

export function useOnEntrySaved(reload: () => void) {
  useEffect(() => {
    window.addEventListener(EVENT_NAME, reload);
    return () => window.removeEventListener(EVENT_NAME, reload);
  }, [reload]);
}
