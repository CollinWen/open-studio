/**
 * SiteFooter: the last line, under a double rule of the page: the studio
 * mark and the year, then a link to the about page and, at the far end, the
 * light/dark pick (ThemeChoice). (The way into the studio is in the header.)
 * Pointing at the mark plays its sweep.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";
import { StudioMark } from "./StudioMark";
import { ThemeChoice } from "./ThemeChoice";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <LabelRow rule="double">
        <div className="site-footer-line">
          <p className="word-list quiet">
            <span className="site-footer-sign">
              <StudioMark />© {new Date().getFullYear()}
            </span>
            <Link to="/about">about</Link>
          </p>
          <ThemeChoice />
        </div>
      </LabelRow>
    </footer>
  );
}
