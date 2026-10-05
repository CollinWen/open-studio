"""
Settings: every value the backend reads from the environment, in one place.

Values come from backend/.env (see .env.example) or the shell. Nothing else
in the backend reads environment variables directly.
"""

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    """Read backend/.env as KEY=VALUE lines. Values already set in the shell win."""
    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Owner access: the password-like token for the admin page and capture API.
    owner_token: str = os.environ.get("OWNER_TOKEN", "")

    # OpenRouter: one key covers both the tag model and the embedding model.
    openrouter_api_key: str = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    tag_model: str = os.environ.get("TAG_MODEL", "z-ai/glm-5.3-flash")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")

    # Local storage: the database file and uploaded images.
    data_dir: Path = Path(os.environ.get("DATA_DIR", BACKEND_DIR / "data"))

    # Which website is allowed to call this API from a browser.
    frontend_origin: str = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    @property
    def database_path(self) -> Path:
        return self.data_dir / "studio.db"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"


settings = Settings()
