/**
 * SiteFooter: the last row, under a double rule of the page: the year in the label
 * column, then a link to the about page. (The way into the studio is in the header.)
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <LabelRow rule="double" label={`© ${new Date().getFullYear()}`}>
        <span className="quiet">
          <Link to="/about">about</Link>
        </span>
      </LabelRow>
    </footer>
  );
}
