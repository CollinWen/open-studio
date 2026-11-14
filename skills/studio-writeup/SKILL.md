---
name: studio-writeup
description: Write an HTML page for an Open Studio entry (a write-up) — a findings report, what a commit or prototype changed, a comparison, a diagram — knowing exactly how much room the page has, what the studio keeps, and what it takes over. Use whenever you're about to write HTML for the studio, or attach one with attach_writeup.
---

# Writing HTML pages for the studio

A write-up is a page of HTML on an entry. It's for whatever a few sentences of
description can't carry: a study's findings with a table, what a commit
changed and why, a side-by-side comparison, a diagram of how something flows.
The studio shows it on the entry's page, in the site's own type, grid and
paper (light or dark, as the visitor picked).

You have a lot of room for **what the page says and how it's arranged**. You
have none over **how it looks**, and nothing on it can run.

## How much room you have

| | Who decides | What that covers |
|---|---|---|
| **Yours** | What's on the page and how it's arranged | Any structure: headings, lists, tables, figures, code, `details`. Layout: columns, grids, flex rows, widths, alignment, gaps, order. Drawings: inline SVG with any geometry, arrowheads, hatching, reused shapes, labels. Pictures written into the file. Links out. |
| **The studio's** | How it looks | The typeface, every type size, every color and background, borders, shadows, rounded corners, and the space between blocks (margins, padding). These come from the studio's own stylesheet and replace whatever you write. |
| **Nobody's** | Anything that runs or loads | Scripts, event handlers (`onclick`...), forms and inputs, `iframe`, `video`, `audio`, `canvas`, `object`, and anything fetched from another address: stylesheets, fonts, pictures, `@import`, `url(...)`. |

So write the page as if a very good designer will set it for you: give it
clear structure and a sensible arrangement, and let the look go. Don't spend
effort on colors, fonts, cards, shadows or a CSS framework. They're removed,
and the answer from `attach_writeup` lists each thing it removed. If something
you needed was removed, find a plainer way to say it. Don't try to get around it.

Nothing on the page can be interactive: no tabs, toggles you script, hover
charts or live data. `details` and `summary` (open and close by clicking) are
the one exception, because the browser does them without a script. A diagram
library that draws in the browser (Mermaid, D3, Chart.js) can't run here, so
draw the finished SVG yourself.

## Structure

- `h1` once, at the top: the thing's name. Then a `p class="lead"` that gives
  the answer first.
- `h2` for each section (the studio starts each one under a rule), `h3` within,
  `h4` for a small label.
- `p`, `ul`, `ol`, `li`, `dl`, `dt`, `dd`, `blockquote`, `cite`, `q`, `em`,
  `strong`, `small`, `sub`, `sup`, `mark`, `abbr`, `hr`, `br`.
- Tables: `table`, `caption`, `thead`, `tbody`, `tfoot`, `tr`, `th` (with
  `scope`), `td` (with `colspan` and `rowspan`). They're set like the site's
  lists: small column names and hairline rows.
- Code: `pre` and `code`, in the same typeface as the text.
- Grouping: `section`, `article`, `header`, `footer`, `aside`, `div`, `span`;
  `id`, `class`, `title`, `role`, `aria-label` and `aria-hidden` on anything.
- Tags not on this page are removed, but their text stays.

## Layout

Use `<style>` blocks or `style=""` with your own class names. Only these
properties are kept; every other declaration is removed:

- **Boxes:** `display` (block, flex, grid, none...), `width`, `min-width`,
  `max-width`, `height`, `min-height`, `max-height`, `aspect-ratio`.
- **Flex and grid:** `flex` and its parts, `grid-template-columns`,
  `grid-template-rows`, `grid-template-areas`, `grid-column`, `grid-row`,
  `grid-area`, `grid-auto-flow`, `gap`, `row-gap`, `column-gap`, `order`,
  `justify-*`, `align-*`, `place-*`.
- **Text and flow:** `text-align`, `vertical-align`, `white-space`,
  `columns`, `column-count`, `column-width`, `break-inside`, `break-before`,
  `break-after`, `list-style-type`, `table-layout`, `overflow-x`.
- **Pictures:** `object-fit`, `object-position`.
- `@media` blocks are kept (filtered the same way), so a layout can fold to one
  column on a phone. Every other `@` rule is removed.

To stay on the studio's grid, size gaps with its units: `var(--line)` (one
line of text, the vertical unit) and `var(--gutter)` (the space between
columns). Running text keeps a readable width on its own; a `figure`, `table`
or `pre` with `class="wide"` uses the full width.

## Drawings

Inline `<svg>` with `g`, `path`, `line`, `polyline`, `polygon`, `rect`,
`circle`, `ellipse`, `text`, `tspan`, plus `defs`, `marker` (arrowheads),
`pattern` (hatching) and `symbol` and `use` (draw a shape once, place it many
times). Any geometry is kept: `viewBox`, coordinates, `d`, `points`,
`transform`, `stroke-width`, `stroke-dasharray`, `marker-end`, `refX`, and so on.

- **Ink only.** Lines are drawn in the page's ink. Fill a shape with
  `fill="currentColor"`, leave it open with `fill="none"`, or hatch it with
  `fill="url(#your-pattern)"`. `class="soft"` and `class="faint"` give the
  lighter inks. No other colors: tell things apart with fills, hatching,
  dashes (`stroke-dasharray`) and labels.
- References like `url(#arrow)` and `href="#shape"` must point inside the same
  drawing. Nothing outside it can be referenced.
- Labels are set in the page's small size. Give the `svg` a `width` and
  `height` equal to its `viewBox` so they show at that size.
- Give each drawing `role="img"` and an `aria-label` that says what it shows.

## Pictures and links

- Pictures go in the file: `<img src="data:image/png;base64,...">` (png, jpeg,
  gif or webp), inside a `figure` with a `figcaption`. A picture from a web
  address is removed. The whole write-up must be under 5 MB.
- Links: `a href` to `https://`, `http://` or `mailto:` (they open in a new
  tab), `#an-id` on the same page, or `/entry/<id>` for another entry in the
  studio (it opens on the studio's own page). Link what the page mentions to
  the entries the studio has on it: how is in the `linking-entries` skill.

## Attaching one

1. Add the entry first (`add_entry`). Its **description** still matters most:
   it's what the owner reads in the grid. The write-up's words also feed the
   entry's tags, its Related entries and search, so write the text plainly.
2. `attach_writeup(entry_id, html, caption="")`. Send only the page's content;
   `<html>`, `<head>` and `<body>` aren't needed. If the entry has no pictures,
   the grid shows a typographic cover (its title, set large).
3. Read `removed` in the answer. An empty list means everything was kept.

Without MCP, the owner can upload the same HTML as a `.html` file in the
entry form; it goes through the same rules.

## Writing well for the studio

- Answer first, then support it. One idea per `h2`.
- Prefer a table or a drawing to a paragraph of numbers.
- Use a layout when it helps reading (two options side by side, a diagram
  beside its notes), not to decorate.
- Every picture earns its place: the work itself, or a figure that shows what
  words can't. Caption it.
- End with where it came from: sources, the commit, the entries it builds on
  (link those with `builds_on` too, not only in the text).

`example.html` in this folder uses all of this (a table, a two-column
layout, a chart, and a flow diagram with arrowheads and hatching) and comes
through with nothing removed. Start from it.
