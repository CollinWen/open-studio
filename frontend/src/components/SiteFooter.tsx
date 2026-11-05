/**
 * SiteFooter: the last row, under a double rule of the page: the studio mark
 * and the year in the label column, then a link to the about page and, at
 * the far end, the light/dark pick (ThemeChoice). (The way into the studio
 * is in the header.) Pointing at the mark plays its sweep.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";
import { StudioMark } from "./StudioMark";
import { ThemeChoice } from "./ThemeChoice";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <LabelRow
        rule="double"
        label={
          <span className="site-footer-sign">
            <StudioMark />© {new Date().getFullYear()}
          </span>
        }
      >
        <div className="site-footer-line">
          <span className="quiet">
            <Link to="/about">about</Link>
          </span>
          <ThemeChoice />
        </div>
      </LabelRow>
    </footer>
  );
}
