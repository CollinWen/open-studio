/**
 * ThemeChoice: "auto · light · dark", the visitor's pick of paper. Kept in
 * this browser (localStorage), so it stays on every visit; "auto", the
 * default, follows the system's light or dark setting and changes with it.
 *
 * Sets data-theme on <html>; global.css holds the dark tokens. index.html
 * applies the saved pick before the first paint (no flash of the wrong
 * paper) and reads the same key, so change both together. Used by SiteFooter.
 */

import { useEffect, useState } from "react";
import { WordChoice } from "./WordChoice";

const THEMES = ["auto", "light", "dark"] as const;
type Theme = (typeof THEMES)[number];

const STORAGE_KEY = "open-studio-theme";
const SYSTEM_DARK = "(prefers-color-scheme: dark)";

export function ThemeChoice() {
  const [theme, setTheme] = useState<Theme>(readSavedTheme);

  useEffect(() => {
    const system = window.matchMedia(SYSTEM_DARK);
    const apply = () => {
      const dark = theme === "dark" || (theme === "auto" && system.matches);
      document.documentElement.dataset.theme = dark ? "dark" : "light";
    };
    apply();
    system.addEventListener("change", apply);
    return () => system.removeEventListener("change", apply);
  }, [theme]);

  const pick = (next: Theme) => {
    setTheme(next);
    try {
      if (next === "auto") localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage can be blocked (private windows); the pick still holds for this visit.
    }
  };

  return (
    <span className="word-list" role="group" aria-label="Paper">
      {THEMES.map((name) => (
        <WordChoice key={name} label={name} active={theme === name} onPick={() => pick(name)} />
      ))}
    </span>
  );
}

function readSavedTheme(): Theme {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === "light" || saved === "dark" ? saved : "auto";
  } catch {
    return "auto";
  }
}
