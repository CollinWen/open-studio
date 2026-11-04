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

## Where the site stands (audit, November 2026)

**Not present:** italics (2), Instrument Serif (3), diagrams (9), code breadcrumbs (11), section numbers (12), squircles (14), mono (15), all caps (16), gradients (17). Keep them out unless the owner asks.

**Present, and waiting on the owner's decision:**

- **Pills (1, 8).** Tags sit in thin rounded ovals with a border (`.oval`). They're the one bordered shape on the site, chosen so a tag reads as pickable. Open: is the oval yours, or a default we picked up?
- **Tight kerning (4).** The display intro is set at `-0.035em`, the site name at `-0.01em` (`global.css`, `.display` and `.site-header`). Open: is the poster-tight intro part of the voice?
- **Detail (5).** A board page carries the section line with counts, a shaded control band, a caret, size dots, a month-bar time slider and the sphere. Open: which of these do you use, and which are there because they could be?
- **Dividers (6).** Every section starts with a full-width rule (double or single). Inside sections there are also hairlines between related entries, between ledger rows, above the control band and under every text field. Open: what is a rule *for* on this site?
- **Shades and opacities (7).** Two ink strengths (`--ink-soft` 52%, `--ink-faint` 18%) plus a shaded paper, and seven different one-off fades in components (0.12, 0.15, 0.25, 0.35, 0.4, 0.82). The one-offs break the "change the look through tokens" rule however this is decided. Open: how many levels of "quieter" does the site need?
- **Eyebrows (13).** The label column ("Entry", "About", "Studio", "Tag") hangs beside each display intro; on phones it moves above it, which makes it a literal eyebrow. Open: is the label part of the Swiss grid you want, or does the intro speak for itself?
- **Periods in titles (18).** Every display intro ends in a period: "The back room.", "What the agents are working on.", "Everything tagged “bread”." Open: are intros sentences you're saying, or titles?
- **Verbose text (10).** Mostly lean. Watch the not-found line and generated tag intros.

## Decisions

Record each answer here: the pattern, what was decided, and the reason in the owner's words. Newest at the bottom.

- *(none yet)*
