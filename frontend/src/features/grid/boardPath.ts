/**
 * boardPath: the address of a board's page. The home board is the site's
 * front page ("/"); every other board lives at "/b/<slug>".
 *
 * Used by BrowsePanel, EntryPage, the agents page and the entry form.
 */

export const HOME_BOARD = "home";

export function boardPath(slug: string): string {
  return slug === HOME_BOARD ? "/" : `/b/${slug}`;
}
