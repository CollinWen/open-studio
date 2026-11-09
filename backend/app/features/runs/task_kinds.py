"""
Task kinds and outside tools: what the owner can give an agent to do, and
what each kind of task may reach beyond the studio.

Task kinds (the offerings):
  study       - one source (a reel, an article, a talk): pull out what it says,
                then find a few related sources worth the owner's time
  references  - work in progress: other directions, prior work and studies,
                what others have made; a reference shelf, like a mood board
  prototype   - an idea: a new repository with a first working sketch, and an
                entry recording what was tried

Outside tools are what a run may use beyond the studio. The studio can't
enforce them itself (it never runs them); they are written into the run's
token and kit, and the harness that runs the agent (Claude Code, a box)
allows only those. The studio's own tools are always there. What "github"
can reach is really decided by the GitHub credentials the harness holds
(best: a GitHub App allowed only on new repositories), since "code" gives a
shell that can run git and gh too.

The instructions here are the run's prompt; run_kit.py puts them together.
The full guide to judging a source is skills/finding-sources/SKILL.md;
SOURCE_TESTS is its short form, for harnesses without skills. Keep them in step.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OutsideTool:
    description: str
    # The Claude Code tools (permission rules) that give an agent this, for the kit's command.
    claude_code_tools: tuple[str, ...]


OUTSIDE_TOOLS: dict[str, OutsideTool] = {
    "web": OutsideTool("search the web and read pages", ("WebSearch", "WebFetch")),
    "code": OutsideTool("write and run code in its own sandbox", ("Bash", "Edit", "Write")),
    "github": OutsideTool(
        "create one new GitHub repository and push to it",
        ("Bash(gh repo create:*)", "Bash(git:*)"),
    ),
}


@dataclass(frozen=True)
class TaskKind:
    title: str
    # The outside tools it gets unless the run asks for fewer.
    tools: tuple[str, ...]
    instructions: str


SOURCE_TESTS = """\
Judge every source before you add it, on four tests, and add only what passes all four:
- Credibility: the maker has provable standing or long, real experience in this.
- Novelty: it says something new (an approach, a perspective) that shows real thought.
- Execution: made with care and detail; the message comes across; it is worth learning from.
- Value to the owner: it fits what they're working on, or opens a door they hadn't
  considered, and leaves room to explore rather than closing the subject.
In the entry's description, say in a sentence why it passed. Log a finding for good
candidates you turned down and why, so the owner can see your judgement."""

TASK_KINDS: dict[str, TaskKind] = {
    "study": TaskKind(
        title="Study a source",
        tools=("web",),
        instructions="""\
The owner handed you one source: the starting entry, or the link in their note.
1. Read or watch it closely. Write a finding with its key points: the claims, the
   technique, the names and works it mentions.
2. If it isn't in the studio yet, add it, with a description of what it is and why it matters.
3. Find 3 to 6 related sources worth the owner's time: where its ideas come from,
   who answers or extends it, the best treatment of the same question. Add each,
   building on the source (or on each other).
4. Finish with a summary: what the source says, and the reading order you'd suggest.""",
    ),
    "references": TaskKind(
        title="Gather references",
        tools=("web",),
        instructions="""\
The owner has work in progress (the starting entry and its chain) and wants a reference
shelf: other directions it could take, studies and prior work, what others have made.
1. Read the starting entry, its chain and related entries until you understand the
   direction and the owner's taste.
2. Log a plan naming 3 or 4 avenues to look down (an older technique, a neighbouring
   field, a maker who did something close, research on the question).
3. For each avenue add the best one or two sources, building on the starting entry,
   with a description that says what the owner could take from it.
4. Finish with a summary: the avenues, the strongest find in each, and open questions.""",
    ),
    "prototype": TaskKind(
        title="Start a project",
        tools=("web", "code", "github"),
        instructions="""\
The owner has an idea (the starting entry, or their note) and wants it off the ground.
1. Log a plan: the smallest version that shows whether the idea works.
2. Create one new repository named after the idea (private unless the note says
   otherwise) and build that first working sketch, with a README saying what it
   does, how to run it and what's next.
3. Add one entry (kind "project") on the board, linked to the repository, building
   on the starting entry: what you tried, what worked, what didn't, the next steps.
   The owner will brainstorm from this entry, so leave the open questions in it.
4. Finish with a summary and the repository's address.""",
    ),
}
