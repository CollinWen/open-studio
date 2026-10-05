"""
Entry point for the backend. Creates the app, registers every feature's
routes under /api, and serves uploaded images under /media.

Run with:  uvicorn app.main:app --reload   (from the backend/ folder)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_tables
from app.features.capture.routes import router as capture_router
from app.features.entries.routes import router as entries_router
from app.features.media.routes import router as media_router
from app.features.related.routes import router as related_router
from app.features.search.routes import router as search_router
from app.features.tags.routes import router as tags_router

app = FastAPI(title="Open Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(entries_router, prefix="/api")
app.include_router(related_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(capture_router, prefix="/api")
app.include_router(search_router, prefix="/api")

settings.media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
