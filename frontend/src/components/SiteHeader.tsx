/**
 * SiteHeader: the top line of every page, drawn once by App so it stays
 * while pages change and load. It sticks to the top of the screen on solid
 * paper (the graph paper doesn't run under it), closed by the double rule
 * that separates it from the page. On the left, my name (which goes
 * home, the index) and "about"; on the far right, the way into the
 * studio: "owner" goes to the studio page, where the owner signs in; once
 * signed in it reads "studio", with a plus beside it.
 *
 * The plus (add an entry) adds `?add` to the current address, which opens
 * the entry form over whatever page you're on
 * (see features/studio/EntryFormModal.tsx).
 * The page you're on is highlighted the way every pick is: its word sits
 * on the accent square (about, studio).
 * Not here: counts and loading. A board's count sits beside its name in the
 * section line; a view on its way shows the studio mark where it will be.
 */

import { Link, NavLink, useLocation } from "react-router-dom";
import { isOwnerSignedIn } from "../api/ownerSignIn";
import { Icon } from "./Icon";

const navWord = ({ isActive }: { isActive: boolean }) => (isActive ? "square is-current" : "square");

export function SiteHeader() {
  const isOwner = isOwnerSignedIn();
  const location = useLocation();
  const withAdd = new URLSearchParams(location.search);
  withAdd.delete("edit");
  withAdd.set("add", "");

  return (
    <header className="site-header">
      <nav className="site-nav">
        <Link to="/" className="site-name">
          Collin Wen
        </Link>
        <NavLink to="/about" className={navWord}>
          about
        </NavLink>
      </nav>
      <nav className="site-nav" aria-label="studio">
        <NavLink to="/studio" className={navWord}>
          {isOwner ? "studio" : "owner"}
        </NavLink>
        {isOwner && (
          <Link to={{ search: withAdd.toString() }} replace className="icon-button" aria-label="add an entry">
            <Icon name="plus" />
          </Link>
        )}
      </nav>
    </header>
  );
}
