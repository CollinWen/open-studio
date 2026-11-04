/**
 * NotFoundPage (any address no other route matches): says there's nothing
 * here and links back to the index, so a mistyped or old link never lands
 * on a blank page.
 *
 * Used by App.tsx as the last route. Missing entries and boards are handled
 * by their own pages.
 */

import { Link } from "react-router-dom";
import { LabelRow } from "../components/LabelRow";
import { SiteFooter } from "../components/SiteFooter";
import { SiteHeader } from "../components/SiteHeader";

export function NotFoundPage() {
  return (
    <>
      <SiteHeader />
      <main>
        <LabelRow rule="double" label="Not found">
          <p className="quiet">
            Nothing here. <Link to="/">Back to the index.</Link>
          </p>
        </LabelRow>
      </main>
      <SiteFooter />
    </>
  );
}
