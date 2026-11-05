/**
 * SiteHeader: the top line of every page. On the left, my name and the
 * words of navigation (index, about); on the far right, the way into the
 * studio: "owner" goes to the studio page, where the owner signs in; once
 * signed in it reads "studio", with a plus beside it.
 *
 * The plus (add an entry) adds `?add` to the current address, which opens
 * the entry form over whatever page you're on
 * (see features/studio/EntryFormModal.tsx).
 * Not here: counts and loading. A board's count sits beside its name in the
 * section line; a view on its way shows the studio mark where it will be.
 */

import { Link, NavLink, useLocation } from "react-router-dom";
import { readOwnerToken } from "../api/ownerToken";
import { Icon } from "./Icon";

export function SiteHeader() {
  const isOwner = Boolean(readOwnerToken());
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
        <NavLink to="/" end>
          index
        </NavLink>
        <NavLink to="/about">about</NavLink>
      </nav>
      <nav className="site-nav" aria-label="studio">
        <NavLink to="/studio">{isOwner ? "studio" : "owner"}</NavLink>
        {isOwner && (
          <Link to={{ search: withAdd.toString() }} className="icon-button" aria-label="add an entry">
            <Icon name="plus" />
          </Link>
        )}
      </nav>
    </header>
  );
}
