/**
 * SiteFooter: the last row, under the page's closing double rule: the year,
 * then a link to the about page. (The way into the studio is in the header.)
 */

import { Link } from "react-router-dom";
import { PageRow } from "./PageRow";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <PageRow rule="double">
        <p className="word-list quiet">
          <span>© {new Date().getFullYear()}</span>
          <Link to="/about">about</Link>
        </p>
      </PageRow>
    </footer>
  );
}
