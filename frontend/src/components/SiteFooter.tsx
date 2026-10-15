/**
 * SiteFooter: the last row, under a double rule of the page: the year in the label
 * column, then the way into the owner's studio page.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "./LabelRow";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <LabelRow rule="double" label={`© ${new Date().getFullYear()}`}>
        <span className="quiet">
          <Link to="/about">about</Link>
          {" · "}
          <Link to="/studio">owner</Link>
        </span>
      </LabelRow>
    </footer>
  );
}
