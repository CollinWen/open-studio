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
token and kit, and whatever harness runs the agent allows only those
(harness-specific setups, such as claude_code_setup.py, translate them). The studio's own tools are always there. What "github"
can reach is really decided by the GitHub credentials the harness holds
(best: a GitHub App allowed only on new repositories), since "code" gives a
shell that can run git and gh too.

The instructions here are the run's prompt; run_kit.py puts them together.
The full guide to judging a source is skills/gathering-sources/SKILL.md;
SOURCE_TESTS is its short form, for harnesses without skills. Keep them in step.
Each kind also names the skills (in skills/) an agent should load for it.
"""

from dataclasses import dataclass

# Each outside tool, and what it lets a run do.
OUTSIDE_TOOLS: dict[str, str] = {
    "web": "search the web and read pages",
    "code": "write and run code in its own sandbox",
    "github": "create one new GitHub repository and push to it",
}


@dataclass(frozen=True)
class TaskKind:
    title: str
    # The outside tools it gets unless the run asks for fewer.
    tools: tuple[str, ...]
    # The skills in skills/ for this kind of work, beside open-studio and studio-collaborator.
    skills: tuple[str, ...]
    instructions: str


SOURCE_TESTS = """\
Judge every source by the visible marks of careful thinking, not by polish or effort:
- Credibility (a prior, not a gate): a track record in this area, or work that shows
  deep, checkable knowledge. Outsiders who bridge two fields count.
- Novelty: a new approach or perspective, argued through; old is fine, derivative isn't.
- Execution: worked examples, specific claims that could be wrong, stated limits,
  engagement with objections, density. Quote the passage that earns each score.
- Value to the owner (a separate axis): it hits one of the board's open questions and
  leaves room to explore. A source that matches none is cut, however good.
Add at most three. In the description give what it is, the open question it hits, the
one claim worth testing and a question to hold while reading, not a summary. Log a
finding with your quotes, and one for strong candidates you turned down and why."""

TASK_KINDS: dict[str, TaskKind] = {
    "study": TaskKind(
        title="Study a source",
        tools=("web",),
        skills=("studying-sources", "gathering-sources"),
        instructions="""\
The owner handed you one source: the starting entry, or the link in their note.
1. Read or watch it closely. Write a finding with its key points: the claims, the
   technique, the names and works it mentions.
2. If it isn't in the studio yet, add it, with a description of what it is and why it matters.
3. Find up to three related sources worth the owner's time: where its ideas come from,
   who answers or extends it, the best treatment of the same question. Add each,
   building on the source (or on each other).
4. Finish with a summary: what the source says, and the reading order you'd suggest.""",
    ),
    "references": TaskKind(
        title="Gather references",
        tools=("web",),
        skills=("gathering-sources",),
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
        skills=("building",),
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
