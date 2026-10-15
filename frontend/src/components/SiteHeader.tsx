/**
 * SiteHeader: the top row of every page. My name sits in the label column;
 * the words of navigation start the content column. Anything passed as
 * children sits on the far right (an entry count, an "edit" link).
 *
 * When this browser holds the owner token, an "add" link to the studio page
 * appears too, so adding work is always one click away.
 */

import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";
import { readOwnerToken } from "../api/ownerToken";
import { LabelRow } from "./LabelRow";

export function SiteHeader({ children }: { children?: ReactNode }) {
  const isOwner = Boolean(readOwnerToken());

  return (
    <header className="site-header">
      <LabelRow label={<Link to="/">Collin Wen</Link>}>
        <nav className="site-nav">
          <NavLink to="/" end>
            index
          </NavLink>
          <NavLink to="/about">about</NavLink>
        </nav>
        <span className="site-header-extra">
          {children}
          {isOwner && <Link to="/studio">add</Link>}
        </span>
      </LabelRow>
    </header>
  );
}
