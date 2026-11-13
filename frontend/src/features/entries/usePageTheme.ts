/**
 * usePageTheme: the paper the site is showing now, "light" or "dark", kept
 * current as the visitor changes it (components/ThemeChoice.tsx sets it on
 * <html data-theme>). Used by WriteupView, so a write-up's frame changes with the page.
 */

import { useEffect, useState } from "react";

function readTheme(): string {
  return document.documentElement.dataset.theme ?? "light";
}

export function usePageTheme(): string {
  const [theme, setTheme] = useState(readTheme);
  useEffect(() => {
    const watcher = new MutationObserver(() => setTheme(readTheme()));
    watcher.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => watcher.disconnect();
  }, []);
  return theme;
}
