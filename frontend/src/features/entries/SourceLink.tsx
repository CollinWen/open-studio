/**
 * SourceLink: where an entry came from, on its entry page. The source's
 * name (or, without one, the site's) with an arrow out, and under it the
 * site's address in the small soft ink, so you can see where the link goes
 * before following it. Opens in a new tab. A name with no link is plain text.
 *
 * Used by WallLabel.
 */

export function SourceLink({ name, url }: { name: string; url: string }) {
  if (!url) return <>{name}</>;
  const address = readableAddress(url);
  return (
    <a href={url} target="_blank" rel="noreferrer" className="source-link">
      <span className="source-link-name">{name || address.site}</span> ↗
      <span className="source-link-address">{address.site + address.path}</span>
    </a>
  );
}

/** "https://www.example.com/a/b?c" → site "example.com", path "/a/b". Unreadable links are shown as given. */
function readableAddress(url: string): { site: string; path: string } {
  try {
    const parsed = new URL(url);
    const path = parsed.pathname === "/" ? "" : parsed.pathname.replace(/\/$/, "");
    return { site: parsed.hostname.replace(/^www\./, ""), path };
  } catch {
    return { site: url, path: "" };
  }
}
