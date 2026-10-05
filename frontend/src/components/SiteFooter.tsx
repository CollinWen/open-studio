/**
 * SiteFooter: a quiet line at the bottom of the page, including the way
 * into the owner's studio page.
 */

import { Link } from "react-router-dom";

export function SiteFooter() {
  return (
    <footer className="site-footer quiet">
      <Link to="/about">about</Link>
      {" · "}
      <Link to="/studio">owner</Link>
    </footer>
  );
}
