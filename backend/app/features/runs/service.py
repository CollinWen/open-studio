"""
Run service: starting a run (one task for one agent, with a short-lived token
that says what it may do), describing one, and finishing it.

The rules for what a run may be given:
  - the owner may start a run for any agent; an agent (on its own key) only
    for itself; a run token can't start more runs
  - the agent must be active and signed on to the run's board
  - its outside tools must be among those the owner granted the agent
  - it may start from an entry only if the agent can open that entry
  - its token works for RUN_HOURS (or as asked, up to RUN_HOURS_MAX)

Used by runs/routes.py and agent_server/run_tools.py. The token itself is
made in auth/run_tokens.py; the kit's prompt and command in run_kit.py.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.auth.run_tokens import RunClaims, make_run_token
from app.auth.viewer import Viewer
from app.config import settings
from app.features.agents import service as agents_service
from app.features.boards import service as boards_service
from app.features.entries import service as entries_service
from app.features.runs.models import Run
from app.features.runs.run_kit import build_kit
from app.features.runs.schemas import RunCreate, RunKit, RunOut
from app.features.runs.task_kinds import TASK_KINDS

LIST_LIMIT = 100
SUMMARY_MAX_LENGTH = 4000


class RunNotAllowedError(Exception):
    """The run asks for something its starter or its agent may not have."""


def start_run(db: Session, data: RunCreate, starter: Viewer) -> tuple[Run, str]:
    """The new run and its token (shown once, in the kit)."""
    _check_starter(starter, data.agent)
    agent = agents_service.get_agent(db, data.agent)
    if agent is None or not agent.active:
        raise RunNotAllowedError(f"No active agent {data.agent}")
    agent_viewer = Viewer(role="agent", agent_name=agent.name)

    board = boards_service.get_board(db, data.board)
    if board is None or not boards_service.can_add_to_board(agent_viewer, board):
        raise RunNotAllowedError(f"{agent.name} isn't signed on to board {data.board}")

    tools = list(data.tools) if data.tools is not None else list(TASK_KINDS[data.kind].tools)
    missing = [tool for tool in tools if tool not in agent.tools]
    if missing:
        raise RunNotAllowedError(f"{agent.name} hasn't been granted: {', '.join(missing)}")

    if data.entry_id and entries_service.get_entry(db, data.entry_id, agent_viewer) is None:
        raise RunNotAllowedError(f"{agent.name} can't open entry {data.entry_id} (missing or private)")

    hours = data.hours or settings.run_hours
    if hours > settings.run_hours_max:
        raise RunNotAllowedError(f"A run can last at most {settings.run_hours_max} hours")
    if not settings.run_token_secret:
        raise RunNotAllowedError("Set RUN_TOKEN_SECRET (or OWNER_TOKEN) to start runs")

    run = Run(
        agent=agent.name,
        kind=data.kind,
        board=board.slug,
        brief=data.brief.strip(),
        entry_id=data.entry_id or None,
        tools=tools,
        started_by=starter.added_by,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    claims = RunClaims(run_id=run.id, agent=run.agent, scopes=frozenset(scopes_of(run)), expires_at=_aware(run.expires_at))
    return run, make_run_token(claims)


def make_kit(db: Session, run: Run, token: str, api_url: str) -> RunKit:
    """The kit for a run just started: its token, where to connect, and its prompt."""
    agent_viewer = Viewer(role="agent", agent_name=run.agent)
    start = entries_service.get_entry(db, run.entry_id, agent_viewer) if run.entry_id else None
    api_url = settings.public_api_url or api_url
    return build_kit(describe_run(db, run), run, token, api_url, start)


def scopes_of(run: Run) -> list[str]:
    """What the run's token allows, as written in it."""
    return sorted([f"board:{run.board}", *run.tools])


def get_run(db: Session, run_id: str) -> Run | None:
    return db.get(Run, run_id)


def can_see_run(viewer: Viewer, run: Run) -> bool:
    """The owner, or the agent the run is for (on a run token, only that run)."""
    if viewer.is_owner:
        return True
    return viewer.is_agent and viewer.agent_name == run.agent and viewer.run_id in ("", run.id)


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


def finish_run(db: Session, run: Run, summary: str) -> Run:
    """End the run: its token stops working. Finishing twice keeps the first summary."""
    if run.finished_at is None:
        run.finished_at = datetime.now(timezone.utc)
        run.summary = summary.strip()[:SUMMARY_MAX_LENGTH]
        db.add(run)
        db.commit()
        db.refresh(run)
    return run


def _check_starter(starter: Viewer, agent_name: str) -> None:
    if starter.is_owner:
        return
    if not starter.is_agent or starter.is_run:
        raise RunNotAllowedError("Only the owner, or an agent on its own key, can start a run")
    if starter.agent_name != agent_name:
        raise RunNotAllowedError("An agent can only start runs for itself")


def _state(run: Run) -> str:
    if run.finished_at is not None:
        return "finished"
    return "expired" if _aware(run.expires_at) <= datetime.now(timezone.utc) else "running"


def _aware(moment: datetime) -> datetime:
    # SQLite gives times back without a zone; they were stored in UTC.
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)
