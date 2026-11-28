"""
Run service: issuing a token, which starts a run (one session of one agent,
open or with a task, with a token that says what it may do), describing one,
setting up a sandbox for it, noting where its harness keeps the session, and
finishing it.

The rules for what a run may be given:
  - only the owner issues tokens; a run token can't start more runs
  - the agent must be active and signed on to each of the run's boards (or
    the run reaches all its boards, "*")
  - its add-ons must be its agent's (all of them, unless asked for fewer)
  - it may start from an entry only if the agent can open that entry
  - its token works for RUN_MINUTES (or as asked, up to RUN_MINUTES_MAX)
  - its session link may only go to a site in SESSION_LINK_SITES, and only
    while the run is live

Used by runs/routes.py and agent_server/run_tools.py. The token itself is
made in auth/run_tokens.py; the kit's prompt and lines in run_kit.py; the
sandbox's files and start command in sandbox_setup.py, its AGENTS.md in
agents/agents_md.py.
"""

from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

from sqlmodel import Session, select

from app.auth.run_tokens import RunClaims, make_run_token
from app.auth.viewer import Viewer
from app.config import settings
from app.features.addons import service as addons_service
from app.features.agents import service as agents_service
from app.features.agents.agents_md import write_agents_md
from app.features.agents.models import Agent
from app.features.boards import service as boards_service
from app.features.entries import service as entries_service
from app.features.entries.models import Entry
from app.features.runs.models import Run
from app.features.runs.run_kit import CORE_SKILLS, build_kit, build_prompt, run_skill_names
from app.features.runs.sandbox_setup import build_sandbox_setup
from app.features.runs.schemas import ALL_BOARDS, RunCreate, RunKit, RunOut, SandboxSetup

LIST_LIMIT = 100
SUMMARY_MAX_LENGTH = 4000


class RunNotAllowedError(Exception):
    """The run asks for something its starter or its agent may not have."""


class SessionSiteNotAllowedError(RunNotAllowedError):
    """A session link goes to a site not in SESSION_LINK_SITES."""


def start_run(db: Session, data: RunCreate, starter: Viewer) -> tuple[Run, str]:
    """The new run and its token (shown once, in the kit)."""
    if not starter.is_owner:
        raise RunNotAllowedError("Only the owner issues tokens")
    agent = agents_service.get_agent(db, data.agent)
    if agent is None or not agent.active:
        raise RunNotAllowedError(f"No active agent {data.agent}")
    agent_viewer = Viewer(role="agent", agent_name=agent.name)
    boards = _checked_boards(db, agent_viewer, data.boards)

    addons = _checked_addons(db, agent, data.addons)

    if data.entry_id and entries_service.get_entry(db, data.entry_id, agent_viewer) is None:
        raise RunNotAllowedError(f"{agent.name} can't open entry {data.entry_id} (missing or private)")

    minutes = data.minutes or settings.run_minutes
    if minutes > settings.run_minutes_max:
        raise RunNotAllowedError(f"A token can last at most {settings.run_minutes_max // (24 * 60)} days")
    if not settings.run_token_secret:
        raise RunNotAllowedError("Set RUN_TOKEN_SECRET (or OWNER_TOKEN) to start runs")

    run = Run(
        agent=agent.name,
        kind=data.kind,
        boards=boards,
        brief=data.brief.strip(),
        entry_id=data.entry_id or None,
        addons=addons,
        started_by=starter.added_by,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    claims = RunClaims(run_id=run.id, agent=run.agent, scopes=frozenset(scopes_of(run)), expires_at=_aware(run.expires_at))
    return run, make_run_token(claims)


def make_kit(db: Session, run: Run, token: str, api_url: str) -> RunKit:
    """The kit for a run just started: its token, where to connect, its prompt, and the
    line that sets up a sandbox for it."""
    start, agent = _starting_point_and_agent(db, run)
    return build_kit(
        describe_run(db, run), run, token, _public(api_url), start, agent.skills if agent else [], _sandbox_services(db, run)
    )


def make_sandbox_setup(db: Session, run: Run, harness: str, api_url: str) -> SandboxSetup:
    """What a fresh sandbox writes and runs to start this run in this harness: its prompt,
    skills, AGENTS.md and studio connection. Only while the run is live. Raises
    skills_service.UnknownSkillsError if one of its skills has gone."""
    if _state(run) != "running":
        raise RunNotAllowedError(f"This run has {'finished' if run.finished_at else 'run out'}")
    start, agent = _starting_point_and_agent(db, run)
    agent_skills = agent.skills if agent else []
    api_url = _public(api_url)
    skills = run_skill_names(run, agent_skills)
    addons = [addons_service.describe_addon(addon) for addon in addons_service.find_addons(db, run.addons)]
    agents_md = write_agents_md(
        run.agent, agent.description if agent else "", run.boards, addons,
        agent.addon_instructions if agent else {}, skills,
    )
    prompt = build_prompt(run, start, api_url, agent_skills)
    return build_sandbox_setup(run, harness, prompt, skills, api_url, agents_md, _sandbox_services(db, run))


def preview_agents_md(db: Session, agent: Agent) -> str:
    """The AGENTS.md a run of this agent would get, on all its boards and with all its add-ons."""
    addons = [addons_service.describe_addon(addon) for addon in addons_service.find_addons(db, agent.addons)]
    skills = list(dict.fromkeys([*CORE_SKILLS, *agent.skills]))
    boards = agents_service.agent_boards(db, agent)
    return write_agents_md(agent.name, agent.description, boards, addons, agent.addon_instructions, skills)


def scopes_of(run: Run) -> list[str]:
    """What the run's token allows, as written in it: "board:<slug>" (or "board:*") and
    "addon:<name>" for each of its add-ons."""
    return sorted([*(f"board:{board}" for board in run.boards), *(f"addon:{name}" for name in run.addons)])


def get_run(db: Session, run_id: str) -> Run | None:
    return db.get(Run, run_id)


def can_see_run(viewer: Viewer, run: Run) -> bool:
    """The owner, or the agent on this run's own token."""
    return viewer.is_owner or (viewer.is_agent and viewer.run_id == run.id)


def list_runs(db: Session, agent: str | None = None) -> list[RunOut]:
    """Newest first."""
    query = select(Run).order_by(Run.created_at.desc()).limit(LIST_LIMIT)
    if agent:
        query = query.where(Run.agent == agent)
    return [describe_run(db, run) for run in db.exec(query)]


def describe_run(db: Session, run: Run) -> RunOut:
    return RunOut(
        **run.model_dump(),
        state=_state(run),
        scopes=scopes_of(run),
        added=entries_service.list_entry_ids_added_in_run(db, run.id),
    )


def set_run_session(db: Session, run: Run, url: str) -> Run:
    """Note where the harness keeps this run's session. Only while the run is live,
    and only to an allowed site (SESSION_LINK_SITES)."""
    if _state(run) != "running":
        raise RunNotAllowedError(f"This run has {'finished' if run.finished_at else 'run out'}")
    if not _is_allowed_session_site(url):
        raise SessionSiteNotAllowedError(f"Session links may only go to: {', '.join(settings.session_link_sites)}")
    run.session_url = url
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_run(db: Session, run: Run, summary: str) -> Run:
    """End the run: its token stops working. Finishing twice keeps the first summary."""
    if run.finished_at is None:
        run.finished_at = datetime.now(timezone.utc)
        run.summary = summary.strip()[:SUMMARY_MAX_LENGTH]
        db.add(run)
        db.commit()
        db.refresh(run)
    return run


def _starting_point_and_agent(db: Session, run: Run) -> tuple[Entry | None, Agent | None]:
    """The entry the run starts from (if its agent can open it) and its agent."""
    agent_viewer = Viewer(role="agent", agent_name=run.agent)
    start = entries_service.get_entry(db, run.entry_id, agent_viewer) if run.entry_id else None
    return start, agents_service.get_agent(db, run.agent)


def _sandbox_services(db: Session, run: Run) -> list[str]:
    """The sandbox's own tools the run's add-ons allow (web, code, github), for its harness."""
    return [addon.service for addon in addons_service.find_addons(db, run.addons) if addon.kind == "sandbox"]


def _checked_addons(db: Session, agent: Agent, asked: list[str] | None) -> list[str]:
    """All the agent's add-ons that are still defined, or the ones asked for, each the agent's."""
    has = [addon.name for addon in addons_service.find_addons(db, agent.addons)]
    if asked is None:
        return has
    missing = [name for name in dict.fromkeys(asked) if name not in has]
    if missing:
        raise RunNotAllowedError(f"{agent.name} doesn't have the add-ons: {', '.join(missing)}")
    return list(dict.fromkeys(asked))


def _public(api_url: str) -> str:
    """The address agents reach this API at: PUBLIC_API_URL, or the one the request came in on."""
    return (settings.public_api_url or api_url).rstrip("/")


def _checked_boards(db: Session, agent_viewer: Viewer, asked: list[str]) -> list[str]:
    """The boards as asked, once each is one the agent is signed on to; ["*"] stays as it is."""
    if ALL_BOARDS in asked:
        if len(asked) > 1:
            raise RunNotAllowedError('Give either "*" (all its boards) or a list of boards, not both')
        return [ALL_BOARDS]
    boards: list[str] = []
    for slug in dict.fromkeys(asked):
        board = boards_service.get_board(db, slug)
        if board is None or not boards_service.can_add_to_board(agent_viewer, board):
            raise RunNotAllowedError(f"{agent_viewer.agent_name} isn't signed on to board {slug}")
        boards.append(board.slug)
    return boards


def _is_allowed_session_site(url: str) -> bool:
    if not settings.session_link_sites:
        return True
    host = (urlsplit(url).hostname or "").lower()
    return any(host == site or host.endswith(f".{site}") for site in settings.session_link_sites)


def _state(run: Run) -> str:
    if run.finished_at is not None:
        return "finished"
    return "expired" if _aware(run.expires_at) <= datetime.now(timezone.utc) else "running"


def _aware(moment: datetime) -> datetime:
    # SQLite gives times back without a zone; they were stored in UTC.
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)
