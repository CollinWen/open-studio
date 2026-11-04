/**
 * SiteFooter: the last row, under a double rule of the page: the studio mark
 * and the year in the label column, then a link to the about page. (The way
 * into the studio is in the header.) Pointing at the mark plays its sweep.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";
import { StudioMark } from "./StudioMark";

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
        <span className="quiet">
          <Link to="/about">about</Link>
        </span>
      </LabelRow>
    </footer>
  );
}
