/**
 * WriteupView: a write-up (an entry's illustrated text) on its entry page,
 * read straight on the page as if it were part of it: the studio's own
 * type and grid, the visitor's paper, and a frame that grows to fit, so it
 * never scrolls on its own. A caption, if any, sits underneath.
 *
 * The write-up is shown in a sandboxed frame that can't run anything
 * (no scripts, no forms, no reaching the page around it); writeupPage.ts
 * builds what goes inside. A link to another entry (/entry/<id>, see
 * skills/linking-entries/) opens that entry on this page, like any link on
 * the site; links out open in a new tab. Used by MediaView.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchWriteup } from "../../api/mediaApi";
import { LoadingMark } from "../../components/LoadingMark";
import type { MediaItem } from "../../types/entry";
import { buildWriteupPage } from "./writeupPage";
import { usePageTheme } from "./usePageTheme";

// No allow-scripts: nothing in a write-up can run. Same origin only so this
// page can measure its height and follow its links to other entries; popups
// so its links out can open in a new tab.
const SANDBOX = "allow-same-origin allow-popups allow-popups-to-escape-sandbox";

export function WriteupView({ item, title }: { item: MediaItem; title: string }) {
  const [html, setHtml] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [height, setHeight] = useState(0);
  const frame = useRef<HTMLIFrameElement>(null);
  const theme = usePageTheme();
  const navigate = useNavigate();

  useEffect(() => {
    let current = true;
    fetchWriteup(item.url)
      .then((text) => current && setHtml(text))
      .catch(() => current && setFailed(true));
    return () => {
      current = false;
    };
  }, [item.url]);

  const fitToContent = useCallback(() => {
    const page = frame.current?.contentDocument?.documentElement;
    if (page) setHeight(page.scrollHeight);
  }, []);

  // Refit when the column changes width (the text rewraps) and once the typeface has loaded.
  useEffect(() => {
    const element = frame.current;
    if (!element) return;
    const watcher = new ResizeObserver(fitToContent);
    watcher.observe(element);
    return () => watcher.disconnect();
  }, [html, fitToContent]);

  const onLoad = () => {
    const page = frame.current?.contentDocument;
    fitToContent();
    page?.fonts?.ready.then(fitToContent);
    page?.addEventListener("click", (event) => {
      const path = entryLinkClicked(event);
      if (path) {
        event.preventDefault();
        navigate(path);
      }
    });
  };

  if (failed) return <p className="quiet">This write-up couldn't be loaded.</p>;
  if (html === null) return <LoadingMark />;
  return (
    <figure className="media-view writeup-view">
      <iframe
        ref={frame}
        className="writeup-frame"
        title={item.caption || title}
        sandbox={SANDBOX}
        srcDoc={buildWriteupPage(html, theme)}
        onLoad={onLoad}
        style={{ height }}
      />
      {item.caption && <figcaption className="quiet">{item.caption}</figcaption>}
    </figure>
  );
}

// The /entry/<id> a plain click on a link to another entry goes to; null for
// anything else (links out, links within the page, a click meant for a new tab).
function entryLinkClicked(event: MouseEvent): string | null {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return null;
  const link = (event.target as Element | null)?.closest?.("a");
  const href = link?.getAttribute("href") ?? "";
  return href.startsWith("/entry/") ? href : null;
}
