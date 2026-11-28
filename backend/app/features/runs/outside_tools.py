"""
Outside tools: what a run may use beyond the studio (web, code, github), and
what each lets it do, in the words the run's prompt uses.

The owner grants them per agent; a run gets those or fewer. The studio can't
enforce them itself (it never runs them): they are written into the run's
token and kit, and whatever harness runs the agent allows only those
(harness-specific setups, such as claude_code_setup.py, translate them). The
studio's own tools are always there. What "github" can reach is really
decided by the GitHub credentials the harness holds (best: a GitHub App
allowed only on new repositories), since "code" gives a shell that can run
git and gh too.

Used by run_kit.py; the names are runs/schemas.py's OutsideToolName.
"""

OUTSIDE_TOOLS: dict[str, str] = {
    "web": "search the web and read pages",
    "code": "write and run code in its own sandbox",
    "github": "create one new GitHub repository and push to it",
}
