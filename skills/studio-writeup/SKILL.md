---
name: studio-writeup
description: Write a write-up for an Open Studio entry, an illustrated page of plain HTML (headings, tables, embedded pictures, simple drawings) that the studio shows in its own style. Use when an entry needs more than its description can hold, such as a study's findings, what a commit or prototype changed, or a comparison of sources, and you're adding it with attach_writeup.
---

# Writing a studio write-up

A write-up is an entry's illustrated text: a page you write in plain HTML
that the studio shows on the entry's page, in the site's own type, grid and
paper (light or dark, as the visitor picked). It's for when a few sentences
of description aren't enough: the findings of a study, what a commit
changed and why, a table that compares sources, a small drawing that shows a shape.

**You write the content. The studio supplies the look.** Every write-up looks
like the rest of the site, whoever wrote it. So don't style anything: no
`<style>`, no `style=""`, no fonts, no colors, no class names of your own, no
CSS framework. All of that is removed when you attach the write-up, and what
was removed is listed in the answer. If something you wanted was removed,
write it a plainer way. Don't try to get around it.

## Attaching one

1. Add the entry first (`add_entry`). Its **description** still matters most:
   it's what the owner reads in the grid and what search and Related use. The
   write-up is the longer read behind it.
2. `attach_writeup(entry_id, html, caption="")` with the HTML as a string.
   It goes after the entry's pictures; if the entry has none, the grid shows a
   typographic cover (the title, set large).
3. Read `removed` in the answer. An empty list means everything was kept.

Without MCP, the owner can upload the same HTML as a `.html` file in the entry
form; it goes through the same cleaning.

## What to write

Send only what goes inside the page's body: no `<html>`, `<head>` or `<body>`
needed (they're removed if you send them). Aim for one screen to a few.

Elements that are kept:

- **Text**: `h1` (once, at the top), `h2` for sections (each starts under a
  rule), `h3`, `h4` (a small label), `p`, `ul`, `ol`, `li`, `dl`, `dt`, `dd`,
  `blockquote`, `cite`, `q`, `em`, `strong`, `small`, `sub`, `sup`, `mark`,
  `abbr`, `hr`, `br`, `details` and `summary`.
- **Tables**: `table`, `caption`, `thead`, `tbody`, `tr`, `th` (with `scope`),
  `td` (with `colspan` and `rowspan`). They read like the site's lists: small
  column names, hairline rows. Keep them to a few columns.
- **Code**: `pre` and `code`, shown in the same typeface as the text.
- **Pictures**: `figure`, `figcaption`, and `img` with the picture written
  into the file as a `data:image/png;base64,...` URL (png, jpeg, gif or webp).
  A picture loaded from a web address is removed: a write-up never fetches anything.
  Keep the whole write-up under 5 MB.
- **Drawings**: inline `svg` with `g`, `path`, `line`, `polyline`, `polygon`,
  `rect`, `circle`, `ellipse`, `text` and `tspan`, using geometry only
  (`viewBox`, coordinates, `d`, `points`, `transform`, `stroke-width`,
  `stroke-dasharray`, `text-anchor`). Lines are drawn in the page's ink.
  Use `fill="currentColor"` to fill a shape and `fill="none"` to leave it
  open; no other colors. Give the `svg` a `width` and `height` equal to its
  `viewBox`, so its text shows at the page's small size. Give it `role="img"`
  and an `aria-label` that says what it shows.
- **Links**: `a href` to `https://`, `http://` or `mailto:` (they open in a new
  tab), or to `#an-id` on the same page. Anything else is removed.
- **Structure**: `section`, `article`, `header`, `footer`, `aside`, `div` and
  `span`, plus `id`, `title`, `role`, `aria-label` and `aria-hidden` on any element.

The only class names that mean anything (all others are removed):

| Class | Use it for |
|---|---|
| `lead` | The opening paragraph, set a size larger: the one-sentence answer. |
| `soft` | Second-strength ink: asides, sources, labels in a drawing. |
| `faint` | The lightest ink: guide lines and axes in a drawing. |
| `wide` | A `figure`, `table` or `pre` that should use the full width instead of the text's measure. |

Everything else is removed, contents and all: `script`, `style`, `link`,
`iframe`, `form` and its inputs, `video`, `audio`, `canvas`, `object` and
`embed`. Event handlers (`onclick` and the rest) and `style` attributes are
removed too. Tags not on the list above are dropped, but their text stays.

## Writing well for the studio

- Open with an `h1` that names the thing and a `lead` that gives the answer
  first. The rest supports it.
- Use plain words and short sections. One idea per `h2`.
- Prefer a table or a small drawing to a paragraph of numbers.
- Every picture earns its place: the work itself, or a figure that shows
  something words can't. Caption it.
- End with where it came from: sources, the commit, the entries it builds on
  (link those with `builds_on`, not only in the text).

`example.html` in this folder is a complete write-up that keeps everything
(`removed` comes back empty). Start from it.
