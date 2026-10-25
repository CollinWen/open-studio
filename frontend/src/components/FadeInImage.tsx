/**
 * FadeInImage: a picture that fades in once it has loaded, instead of
 * painting in top to bottom. Takes everything an <img> takes.
 *
 * Used by EntryCover (grid, rows, sphere) and MediaView (entry pages).
 * Looks: .fade-in-image in global.css.
 */

import { useState, type ImgHTMLAttributes } from "react";

export function FadeInImage({ className, ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  const [loaded, setLoaded] = useState(false);
  const classes = ["fade-in-image", loaded && "is-loaded", className].filter(Boolean).join(" ");
  return (
    <img
      {...props}
      className={classes}
      // A picture already in the browser's cache can finish before onLoad is attached.
      ref={(image) => {
        if (image?.complete && image.naturalWidth > 0) setLoaded(true);
      }}
      onLoad={() => setLoaded(true)}
      // A broken picture shows as broken rather than staying invisible.
      onError={() => setLoaded(true)}
    />
  );
}
