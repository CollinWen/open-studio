/**
 * NotFoundPage (any address no other route matches): says there's nothing
 * here and links back to the index, so a mistyped or old link never lands
 * on a blank page.
 *
 * Used by App.tsx as the last route. Missing entries and boards are handled
 * by their own pages.
 */

import { Link } from "react-router-dom";
import { PageRow } from "../components/PageRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";

export function NotFoundPage() {
  return (
    <>
      <SiteHeader />
      <main>
        <PageRow rule="double">
          <p className="quiet">
            Nothing here. <Link to="/">Back to the index.</Link>
          </p>
        </PageRow>
      </main>
      <SiteFooter />
    </>
  );
}
