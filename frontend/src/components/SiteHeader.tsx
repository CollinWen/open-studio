/**
 * SiteHeader: the top row of every page: my name, then the words of
 * navigation (index, about, owner). The agent log isn't here: it's internal,
 * reached from the studio's agents list. "owner" goes to the studio page, where the owner signs in; once
 * signed in it reads "studio". Anything passed as
 * children sits on the far right (an entry count, "loading").
 *
 * When this browser holds the owner token, a plus (add an entry) joins the
 * navigation words. It adds `?add` to the current address, which opens the entry form
 * over whatever page you're on (see features/studio/EntryFormModal.tsx).
 */

import type { ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { readOwnerToken } from "../api/ownerToken";
import { Icon } from "./Icon";
import { PageRow } from "./PageRow";

export function SiteHeader({ children }: { children?: ReactNode }) {
  const isOwner = Boolean(readOwnerToken());
  const location = useLocation();
  const withAdd = new URLSearchParams(location.search);
  withAdd.delete("edit");
  withAdd.set("add", "");

  return (
    <header className="site-header">
      <PageRow>
        <nav className="site-nav">
          <Link to="/" className="site-name">
            Collin Wen
          </Link>
          <NavLink to="/" end>
            index
          </NavLink>
          <NavLink to="/about">about</NavLink>
          <NavLink to="/studio">{isOwner ? "studio" : "owner"}</NavLink>
          {isOwner && (
            <Link to={{ search: withAdd.toString() }} className="icon-button" aria-label="add an entry">
              <Icon name="plus" />
            </Link>
          )}
        </nav>
        <span className="site-header-extra">{children}</span>
      </PageRow>
    </header>
  );
}
