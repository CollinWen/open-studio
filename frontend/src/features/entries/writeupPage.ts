/**
 * writeupPage: wraps a write-up's HTML in the page its frame shows: the
 * studio's own write-up styles (styles/writeup.css), the visitor's light or
 * dark paper, and a content policy that lets nothing load from anywhere
 * except those styles and pictures written into the file.
 *
 * The backend already removed scripts, styles and outside files
 * (features/media/writeup_sanitizer.py); the policy here, and the frame's
 * sandbox in WriteupView, hold even if something slipped through.
 */

import writeupStylesUrl from "../../styles/writeup.css?url";

export function buildWriteupPage(writeupHtml: string, theme: string): string {
  const stylesUrl = new URL(writeupStylesUrl, window.location.href);
  const policy = [
    "default-src 'none'",
    `style-src ${stylesUrl.origin}`,
    `font-src ${stylesUrl.origin}`,
    "img-src data:",
  ].join("; ");
  return `<!DOCTYPE html>
<html lang="en" data-theme="${theme === "dark" ? "dark" : "light"}">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="${policy}">
<link rel="stylesheet" href="${stylesUrl.href}">
</head>
<body>${writeupHtml}</body>
</html>`;
}
