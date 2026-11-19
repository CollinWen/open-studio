---
name: linking-entries
description: Turn a write-up into a wiki-style page by linking the things it mentions to the entries the studio already has on them — search for each one, check it's really the same thing, and write the link in. Use whenever you write or revise a write-up (attach_writeup), so a reader can follow a mention to what the studio holds on it.
---

# Linking a write-up to the studio's entries

A write-up shouldn't be an island. When it mentions something the studio
already holds (a technique, a maker, a paper, an earlier experiment), the words
should link to that entry, the way a wiki page links its terms. A reader then
moves from one idea to the next without searching, and the owner sees how a new
piece touches what's already there.

You can do this now: in a write-up, a link to `/entry/<id>` opens that entry on
the studio's own page. This skill is how to find what to link and how to write
it in. How write-ups look and what they may hold is in `studio-writeup`; load
both.

## What gets linked, and what doesn't

| Link | Don't link |
|---|---|
| A **named thing** the board has an entry on: a work, a person's project, a paper, a technique, an earlier experiment ("the poolish trial", "Tachi's Origamizer"). | Generic words that only share a topic with an entry ("bread", "folding"). That's what tags and Related are for. |
| The **first** time it's mentioned on the page. | Every repeat of it. Once is enough. |
| Entries **on the same board** as the write-up. Boards never mix. | Entries on other boards. If one truly matters, say so in a log `thought` instead. |
| An entry you **read** and know is about the same thing. | A search result you only saw a title of. |

A page with a handful of links reads as a map. A page with a link in every line
reads as noise. As a guide, aim for no more than one link per paragraph.

## Finding the entries

Do this once the text is written and before you attach it.

1. **List the mentions.** Go through your draft and note every named thing a
   reader might want to follow. Include the sources you studied and the entries
   your work builds on.
2. **Search for each one.** `search_studio(query, board=<your board>)`, with
   the thing's own name, then a plainer description of it if nothing comes back.
   Search matches by meaning as well as words, so look past the first result.
3. **Wander from where you are.** `find_related` on the entry the write-up
   belongs to, and `get_chain` on it, often turn up entries you mention but
   wouldn't have thought to search for.
4. **Check before you link.** `get_entry` on the candidate. Read its title,
   description and source. Link only if it is the thing you mean, not merely
   something nearby. If two entries fit, link the one at the original source,
   or the owner's own over an agent's.
5. **Note what's missing.** A mention with no entry stays plain text. If it's
   important to the board, it may be worth adding (see `gathering-sources`), or
   logging as a `thought`. Don't add an entry just so you have something to link.

## Writing the link

Put the link on the words that name the thing, using the entry's id:

```html
<p>The sourdough here started from <a href="/entry/3f2a9c8e1b">the poolish trial</a>,
which had the same slack crumb at 80% water.</p>
```

- Write the address as `/entry/<id>`, exactly. Don't write the site's full
  address: it opens the entry in a new tab, as if it were outside the studio.
- Link the reader's words, not "here" or "this entry". The text should read the
  same with the links taken out.
- Don't add titles, icons or brackets around the link. The studio styles it.
- A link to an entry the reader can't see (an unlisted agent entry, for a
  visitor) leads to a not-found page. That's expected: it starts working when
  the owner publishes the entry.
- Plain descriptions can't hold links yet. Only write-ups can.

## Links and "builds on"

A link in the text says "this page mentions that". A `builds_on` link says
"this work came from that", and it builds the chain. They do different jobs:

- If the entry the write-up belongs to really extends, answers or comes from
  something you linked, also connect them with `builds_on` (in `add_entry`) or
  `link_builds_on`, with a note on how.
- Don't make every mention a `builds_on`. Most mentions are context, not lineage.

## Checking your work

- `attach_writeup` answers with what it `removed`. A link it couldn't keep shows
  up there, and its words stay as plain text. That usually means an address
  other than `/entry/<id>`, `#an-id`, `https://`, `http://` or `mailto:`.
- In your log `finding`, or your run's summary, say which entries the write-up
  links to, so the owner and the other agents see the new connections.
