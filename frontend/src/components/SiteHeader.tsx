/**
 * SiteHeader: the top row of every page. My name sits in the label column;
 * the words of navigation start the content column. Anything passed as
 * children sits on the far right (an entry count, "loading").
 *
 * When this browser holds the owner token, "add" joins the navigation
 * words. It adds `?add` to the current address, which opens the entry form
 * over whatever page you're on (see features/studio/EntryFormModal.tsx).
 */

import type { ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "./LabelRow";

export function SiteHeader({ children }: { children?: ReactNode }) {
  const isOwner = Boolean(readOwnerToken());
  const location = useLocation();
  const withAdd = new URLSearchParams(location.search);
  withAdd.delete("edit");
  withAdd.set("add", "");

  return (
    <header className="site-header">
      <LabelRow label={<Link to="/">Collin Wen</Link>}>
        <nav className="site-nav">
          <NavLink to="/" end>
            index
          </NavLink>
          <NavLink to="/about">about</NavLink>
          {isOwner && <Link to={{ search: withAdd.toString() }}>add</Link>}
        </nav>
        <span className="site-header-extra">{children}</span>
      </LabelRow>
    </header>
  );
}
