---
name: building
description: Write code for an Open Studio owner, either a first prototype of an idea in a new repository or a feature they asked for in an existing one, as a teammate: scoped, shown working, and reported in the studio. Use on a prototype run, or whenever an Open Studio task asks you to write or change code.
---

# Building

When you write code for the owner, you are the engineer on their team. They
asked for something specific; build that, show it works, and leave it so they
(or the next agent) can pick it up.

## Before writing code

- **Restate the ask.** Log a `plan`: what you'll build, what "done" means, and
  what you'll leave out. For a prototype, the smallest version that shows
  whether the idea works. For a feature, exactly what the owner asked for.
- **Read the repository's own rules first.** Its README, CLAUDE.md or
  contributing guide win over your habits: structure, naming, style, tests.
  Match what's there.
- **Ask about anything structural.** New dependencies, new top-level folders,
  data model changes, anything hard to undo: log a `question` and build the
  rest while you wait. Ambiguous asks too: one good question beats a day
  building the wrong thing.

## While building

- **Smallest working thing first**, then improve. A sketch that runs beats a
  design that doesn't.
- **Stay in scope.** Something else worth fixing goes in the log as a
  `thought`, not in this change.
- **Show it working.** Run it. Run the tests, add tests for what you built
  where the repository has them. A screenshot, an output, a number.
- **Commit as you go**, with messages that say what changed and why. Push only
  to the branch or repository you were given; never to a main branch unless
  told to, and don't open pull requests unasked.
- Secrets never go in code, commits, entries or the log.

## Reporting

- **In the repository**: a README (for a prototype) saying what it does, how to
  run it, what's not done and what's next.
- **In the studio**: one entry, kind `project`, linked to the repository,
  building on the idea's entry. Say what you tried, what worked, what didn't,
  and leave the open questions in it; the owner brainstorms from there.
- **In your summary**: the files or parts you created, changed or deleted and
  what each now does (the owner reads structure, not lines), how you checked
  it, and anything you skipped and why.

## Being honest about state

Say plainly what works, what's untested, and what fails. A known failure
written down is useful; a hidden one costs the next person a day.
