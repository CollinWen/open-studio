"""
Entry point for the backend. Creates the app (and the home board, and any
agent named in AGENT_TOKENS, if missing), registers every feature's routes under /api, serves the agent
server (MCP) at /mcp, and serves uploaded images under /media when they are
stored on disk (local development; production uses R2).

Run with:  uvicorn app.main:app --reload   (from the backend/ folder)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.agent_server.server import mount_agent_server, run_agent_server
from app.config import settings
from app.database import create_tables, engine
from app.features.agent_log.routes import router as agent_log_router
from app.features.agents import service as agents_service
from app.features.agents.routes import router as agents_router
from app.features.boards import service as boards_service
from app.features.boards.routes import router as boards_router
from app.features.capture.routes import router as capture_router
from app.features.entries.routes import router as entries_router
from app.features.entry_links.routes import router as entry_links_router
from app.features.media.routes import router as media_router
from app.features.related.routes import router as related_router
from app.features.search.routes import router as search_router
from app.features.tags.routes import router as tags_router

app = FastAPI(title="Open Studio", lifespan=run_agent_server)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()
with Session(engine) as db:
    boards_service.ensure_home_board(db)
    agents_service.ensure_agents_from_settings(db)

app.include_router(entries_router, prefix="/api")
app.include_router(related_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(capture_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(boards_router, prefix="/api")
app.include_router(entry_links_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(agent_log_router, prefix="/api")
mount_agent_server(app)

settings.media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
