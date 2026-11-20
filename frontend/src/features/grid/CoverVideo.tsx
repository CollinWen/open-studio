/**
 * CoverVideo: a video shown as an entry's cover in the grid: silent, on loop,
 * like a moving picture, but playing only while it's on screen (and not at
 * all for visitors who ask for reduced motion), fetching just enough to start.
 * A board can hold many videos; playing and downloading every one at once,
 * on screen or not, keeps a phone's processor and radio busy and hot.
 *
 * Used by EntryCover, for a video with no still of its own.
 */

import { useEffect, useRef } from "react";

export function CoverVideo({ src, label }: { src: string; label: string }) {
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const element = video.current;
    if (!element || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const watcher = new IntersectionObserver(([seen]) => {
      if (seen.isIntersecting) element.play().catch(() => {});
      else element.pause();
    });
    watcher.observe(element);
    return () => watcher.disconnect();
  }, [src]);

  return <video ref={video} className="entry-cover" src={src} muted loop playsInline preload="metadata" aria-label={label} />;
}
