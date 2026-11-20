/**
 * FadeInImage: a picture that fades in once it has loaded, instead of
 * painting in top to bottom. Takes everything an <img> takes. Once loaded
 * it also carries its own shape (width ÷ height) as --image-ratio and its
 * own width as --image-width, so the styles can size its box from them
 * (cards and entry pages round it to whole squares of the graph paper).
 *
 * Used by EntryCover (grid, rows) and MediaView (entry pages).
 * Looks: .fade-in-image in motion.css.
 */

import { useState, type CSSProperties, type ImgHTMLAttributes } from "react";

export function FadeInImage({ className, style, ...props }: ImgHTMLAttributes<HTMLImageElement>) {
  const [loaded, setLoaded] = useState(false);
  const [size, setSize] = useState<{ width: number; ratio: number }>();
  const classes = ["fade-in-image", loaded && "is-loaded", className].filter(Boolean).join(" ");
  const settle = (image: HTMLImageElement) => {
    setLoaded(true);
    const { naturalWidth: width, naturalHeight: height } = image;
    if (width > 0 && height > 0 && size?.width !== width) setSize({ width, ratio: width / height });
  };
  return (
    <img
      // Decode off the main thread, so scrolling past many pictures stays smooth.
      decoding="async"
      {...props}
      className={classes}
      style={size ? ({ ...style, "--image-ratio": size.ratio, "--image-width": `${size.width}px` } as CSSProperties) : style}
      // A picture already in the browser's cache can finish before onLoad is attached.
      ref={(image) => {
        if (image?.complete && image.naturalWidth > 0) settle(image);
      }}
      onLoad={(event) => settle(event.currentTarget)}
      // A broken picture shows as broken rather than staying invisible.
      onError={() => setLoaded(true)}
    />
  );
}
