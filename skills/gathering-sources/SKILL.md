---
name: gathering-sources
description: Find and judge source material worth one person's time to read and study in depth (articles, papers, videos, reels, books, repositories, archives, makers' own pages) on any subject. Scores the visible marks of careful thinking, with quoted evidence, against the owner's open questions, under a hard budget. Use when researching for an Open Studio board or run, digging through archives, gathering references, or deciding whether a source is good enough to recommend.
---

# Gathering sources worth studying

You are choosing what someone will spend real attention on. A short list they
learn from beats a long list they skim. Most of what a search returns fails;
that's expected. Say so and keep looking rather than padding.

**The core idea:** don't score how much effort went into a piece, which you
can't observe. Score the visible marks that careful thinking leaves on the
page. Polish is now nearly free to fake; worked examples, checkable claims
and stated limits are not.

## Where to look

Go toward the people who made the thing, not the people who wrote about it.

- **The original**: the paper, the maker's own site or channel, the book, the
  repository, the recipe from the cook who developed it, the artist's statement.
- **Practitioners' writing**: long posts, talks, workshop notes, process
  videos, forum threads where experts argue in detail.
- **Where taste is kept**: museum and gallery pages, university course pages,
  archives and special collections, respected small publishers, the
  bibliography of a source that already passed.
- **Follow the chain**: who a good source cites, thanks or answers, and who
  later cites it. One strong source usually leads to the next two.
- **Across fields**: the best find is sometimes in a neighbouring field, where
  someone solved the same problem under another name.

Treat as leads at best: listicles, SEO roundups, content farms, reposts without
credit, AI-written summaries, aggregators, anything selling what it reviews.
If a repost is all you can find, find the original before adding it. For a
reel or post you can't fully read, use the caption, the maker's name and the
visible work to find their own site or the source they drew on; add that.

## Step 1. The cheap pre-filter

Before reading closely, drop most of the noise at little cost:

- **Track record** of the maker in *this* area (not credentials in general).
- **Kind and length against claimed substance.** A 90-minute podcast promising
  one idea, a thread claiming a breakthrough, a "complete guide" in 400 words.
- **Durability.** Will this still be worth knowing in five years? News-cycle
  pieces almost never pass.

## Step 2. Score the source, with quotes

Three questions about the source itself. For each, **quote the passage that
earns the score**: the worked example, the stated limit, the falsifiable
claim. No quote, no credit. This keeps you grounded and stops you rewarding
fluent prose, which language-model judges naturally favour.

### Credibility: a prior, not a gate

Does the maker have a track record in this specific area, or does the work
itself show deep, checkable knowledge? Use the answer to set how hard the
other tests must be passed, not to rule sources out. As a gate, credibility
filters out exactly the outsiders who bridge two fields (Don Swanson, an information scientist,
linked fish oil to Raynaud's disease by reading two literatures nobody had
connected). Fail outright only for no traceable maker, borrowed authority
("experts say") or claims that can't be checked.

### Novelty: something new, thought through

A new approach, a perspective you haven't met elsewhere, an argument that
reframes the subject. Old is fine; derivative isn't. The origin of a
well-known idea passes; its hundredth retelling doesn't. Evidence: original
data or cases, a position argued against the strongest objection.

### Execution: the visible marks of careful thinking

Look for these habits of good explainers (Tao, Feynman, Olah):

- **Example before abstraction.** A concrete case built and checked step by
  step; the writer moves up and down the ladder of abstraction (Bret Victor).
  Writing that never comes down to an instance usually means the author never
  built one.
- **The problem before the solution.** You feel why it matters before the
  answer arrives.
- **Specific, checkable claims.** Numbers, named mechanisms, predictions that
  could turn out wrong. Vague writing can't be wrong, which is why it's cheap.
- **Edges marked.** Where the idea fails, what it doesn't cover, what the
  author is unsure of. The most reliable sign of real thinking: you only learn
  where something breaks by pushing on it.
- **Classic style.** The writer shows you something you could see for yourself,
  rather than performing expertise at you (Pinker, after Thomas and Turner).
- **Density.** Most sentences carry a claim you didn't already know. Judge
  density per minute: the same idea in two pages beats it in ninety minutes.

For things that aren't writing, the same marks in other forms: a recipe with
weights and reasons, a process video that shows the failures, code with tests
and a README that says what it doesn't handle.

## Step 3. Relevance to the owner, a separate axis

Steps 1–2 describe the source. This describes the reader; keep them apart, so
a great source that's off-path is recorded as exactly that.

- **Match it to an open problem.** The board's brief (and the run's note) is
  the owner's problem file: the questions they're working on. Feynman's test:
  does this hit one of my open problems? A source that matches none is cut,
  however good it is. Log it as a `finding` in case the questions change.
- **No open questions written down?** Read the brief, the entries and their
  chains, then log a `question` proposing five to fifteen open questions for
  the owner to confirm or rewrite. Work from your list, marked as a guess,
  until they do.
- **Generative beats exhaustive.** Prefer what leaves room to explore, draws a
  parallel they hadn't made, or brings a perspective they should consider.
- **Not already known to them.** Search the studio first.

## Step 4. A hard budget

Unless the brief or note says otherwise, add **at most three sources per run**
(or per session of work). Scarcity forces real ranking: if a fourth is better
than one of your three, swap it in and log why. If nothing passes, say so with
what you searched; that is a useful result.

## Step 5. Hand it over: not a summary

A summary invites the owner to recognise the source instead of reading it.
In the entry's **description** give:

1. **What it is**, in one sentence (who made it, what form, how long).
2. **Which open problem it hits.**
3. **The single claim worth testing**: the one thing to check, argue with, or try.
4. **A question to hold while reading.**

Then log a `finding` with the entry's id and your **evidence**: the quotes
that earned each score, and a line on why it beat the ones you didn't add.

## Step 6. The calibration loop

- **Rejection log.** For every strong candidate you turned down, log a
  `finding` with the test it failed ("Passed on X: well made, but restates Y,
  already on the board"). The owner spot-checks these for false negatives.
- **Learn from what they do.** Which of your entries the owner published, left
  unlisted or built a note on (`list_entries`, by `visibility`). When their
  choices disagree with your scores, log a `thought` saying what you'll weigh
  differently.
- **Reading order.** End your summary with the order you'd read the finds in,
  and why.
