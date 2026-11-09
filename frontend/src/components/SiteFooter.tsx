/**
 * SiteFooter: the last line, under a double rule of the page: the studio
 * mark and the year, then a link to the about page and, at the far end, the
 * light/dark pick (ThemeChoice). (The way into the studio is in the header.)
 * Pointing at the mark plays its sweep. The version the site was deployed
 * as (v0.1.4) sits after the year, so you can see what's live; deploy.py sets it.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";
import { StudioMark } from "./StudioMark";
import { ThemeChoice } from "./ThemeChoice";

const SITE_VERSION = import.meta.env.VITE_STUDIO_VERSION || "dev";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <LabelRow rule="double">
        <div className="site-footer-line">
          <p className="word-list quiet">
            <span className="site-footer-sign">
              <StudioMark />© {new Date().getFullYear()}
            </span>
            <span>{SITE_VERSION}</span>
            <Link to="/about">about</Link>
          </p>
          <ThemeChoice />
        </div>
      </LabelRow>
    </footer>
  );
}
