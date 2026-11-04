# Open Studio: Keeping the Design Mine

This file is for any agent working on how the site looks, reads or feels. CLAUDE.md says **what** the design is; this file says **whose** it is, and how to behave when you touch it.

## The owner's position (in their words, lightly edited)

> I want to make sure the site keeps its human touch, and that there's a call on what I'm personally putting into the design and feel of the site. If you notice yourself falling into subconscious patterns when designing, ask me about it specifically, and ask me guiding design questions. Your role is to help me find my own clarity in my perspective and delivery, and it should be consistent. I don't want the design to roll out of my touch, because the design is an extension of my thought process and workflow.
>
> The list below isn't a hard set of rules. It's the common fallbacks that show up when people let AI take over their design process and squeeze out the human interpretation.

## How to work

1. **The owner makes design decisions; you help them make those decisions on purpose.** Don't settle a question of taste on your own, even a small one (a new fade value, a label, a divider, a heading's wording). Implement what's decided; ask about what isn't.
2. **Catch yourself on the list below.** If a change you're about to make reaches for one of these patterns, stop. Name the pattern to the owner, say why you reached for it, and ask a guiding question ("what should this feel like?", "what would you lose without it?"). Don't ask "should I add X?"
3. **Ask questions that lead to a principle, not a single fix.** A good answer should settle the next ten cases too. Record the answer in "Decisions" below, so the design stays consistent and future agents don't ask again.
4. **Already-decided patterns are fine.** Some items on the list are in the site on purpose (see "Decisions"). Keep them as decided; don't spread them to new places without asking.

## Patterns to watch for

These are the common defaults of AI-led design. Using one isn't wrong; using one without meaning to is.

1. Tags and pills
2. Excessive italics
3. Instrument Serif (or any trendy display serif)
4. Negative letter-spacing (tight kerning)
5. Over-detailed UI: more controls, counts and states than the page needs
6. Overused dividers
7. Many color shades and opacities
8. Containers with borders
9. Over-detailed diagrams
10. Verbose, redundant text
11. Code breadcrumbs (`file.tsx`, paths, `snake_case` showing in the UI)
12. Section numbering (01, 02, ...)
13. Eyebrows (a small label over a heading)
14. Squircles (soft rounded rectangles)
15. Too many monospace fonts
16. All-caps subtitles
17. Gradient backgrounds
18. Periods at the end of titles

## Where the site stands

**Not present:** italics (2), Instrument Serif (3), diagrams (9), code breadcrumbs (11), section numbers (12), squircles (14), mono (15), all caps (16), gradients (17). Keep them out unless the owner asks.

**Settled:** pills (1, 8), kerning (4), dividers (6), shades (7), eyebrows and side labels (13), the agents menu item (5). See "Decisions".

**Still open:**

- **Intro wording and periods (10, 18).** Waiting on the owner's own words (see Decisions). Until then, leave the current lines alone and don't write replacements.
- **Detail (5).** Beyond the agents link, nobody has looked at which board controls get used yet (counts in brackets, size dots, the time slider's month bars).
- **The "related" heading.** With the labels gone, the related list on an entry page sits under one quiet word, "related", in body size. Check that this doesn't creep back into being an eyebrow.
- **Ledger column names.** Lists in the studio and on /agents still have small column names over their columns. They're list headers, not side labels, but they're the closest thing left to the form feel the owner disliked.

## Decisions

Record each answer here: the pattern, what was decided, and the reason in the owner's words. Newest at the bottom.

- **Tags (1, pills).** No ovals: they "seem a little trite". Underlined plain words are right, but a wrapped line of them felt chaotic. Tags are a *list* in aligned columns that you read down like an index (`.word-columns`); picked is underlined. Reason: "navigating a list of things might be easier than seeing a bunch of words wrapped across a few rows". Use the same list for any group of words someone browses.
- **Rules (6, dividers).** "A line might only be needed for separating the portions of the website; they serve as canvases for switching context. But within these contexts I would like the interaction to be smooth, like seeing related posts, or just seeing the metadata of an entry." So: a double rule frames the site, a single rule starts a new part of a page, and inside a part only space separates things. No hairlines between list rows, related entries or the control band.
- **Shades (7).** Five ink strengths, as tokens (`--strength-full / soft / muted / faint / ghost`); every quieter color and fade uses one of them, never a one-off number. The owner is open to fewer if someone makes the case. The shaded paper and the existing color gradations stay as they are for now.
- **Intros (10, 18).** Intros are for the visitor and need rephrasing, but the owner writes them: the personal statement, the board descriptions and the page intros are creative direction. Agents don't draft or "improve" this copy unless asked.
- **Side labels (13, eyebrows).** Removed everywhere. "They're informative, but it almost feels like a form that is kind of constricting and not super meaningful to the delivery of the message." The labelling column isn't a point of emphasis, so content starts at the left margin and says what it is (look at how online galleries do it). Don't add labels beside or above content to explain it; if something needs explaining, rethink the thing.
- **Kerning (4).** Normal letter-spacing everywhere. Not a focus for the owner; don't tighten type to make it feel designed.
- **Agents in the menu (5).** Not in the public menu: it's internal. The log is reached from the studio's agents list ("log"). Board pages no longer list their agents.
