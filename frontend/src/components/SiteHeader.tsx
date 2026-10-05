/**
 * SiteHeader: my name (the site title) and a few words of navigation across the top
 * of every page. Anything passed as children sits on the right.
 *
 * When this browser holds the owner token, an "add" link to the studio page
 * appears too, so adding work is always one click away.
 */

import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { readOwnerToken } from "../api/ownerToken";

export function SiteHeader({ children }: { children?: ReactNode }) {
  const isOwner = Boolean(readOwnerToken());

  return (
    <header className="site-header">
      <span>
        <Link to="/">Collin Wen</Link>
        <span className="quiet"> · </span>
        <Link to="/about" className="quiet">
          about
        </Link>
      </span>
      <span className="quiet">
        {children}
        {isOwner && (
          <>
            {children && " · "}
            <Link to="/studio">add</Link>
          </>
        )}
      </span>
    </header>
  );
}
