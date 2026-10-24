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

    # Agents: other programs (a Claude session, a research bot) that may read the
    # studio and add entries. They're managed on the studio page; this is only a
    # starting list, added on startup when missing. Comma-separated name=token
    # pairs, e.g. "scout=long-random-token,archivist=another-token".
    agent_tokens_setting: str = os.environ.get("AGENT_TOKENS", "")
    # How many entries one agent may add or edit per hour. Each write costs an LLM call.
    agent_writes_per_hour: int = int(os.environ.get("AGENT_WRITES_PER_HOUR", "60"))
    # How many lines one agent may write to the agent log per hour (plans, thoughts, findings).
    agent_log_lines_per_hour: int = int(os.environ.get("AGENT_LOG_LINES_PER_HOUR", "120"))

    # OpenRouter: one key covers both the tag model and the embedding model.
    openrouter_api_key: str = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    tag_model: str = os.environ.get("TAG_MODEL", "z-ai/glm-5.3-flash")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")

    # Local storage: the database file, and uploaded images when R2 isn't set up.
    data_dir: Path = Path(os.environ.get("DATA_DIR", BACKEND_DIR / "data"))

    # Which websites may call this API from a browser. Comma-separated for several
    # (e.g. your domain and the Firebase default address).
    frontend_origin: str = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    # Cloudflare R2 (production media storage). Leave empty to store uploads on disk.
    r2_account_id: str = os.environ.get("R2_ACCOUNT_ID", "")
    r2_access_key_id: str = os.environ.get("R2_ACCESS_KEY_ID", "")
    r2_secret_access_key: str = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    r2_bucket: str = os.environ.get("R2_BUCKET", "")
    # The bucket's public address, e.g. https://media.yourdomain.com
    media_public_url: str = os.environ.get("MEDIA_PUBLIC_URL", "")

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    @property
    def agent_tokens(self) -> dict[str, str]:
        """Each agent's token mapped to its name."""
        pairs = (pair.split("=", 1) for pair in self.agent_tokens_setting.split(",") if "=" in pair)
        return {token.strip(): name.strip() for name, token in pairs if name.strip() and token.strip()}

    @property
    def r2_enabled(self) -> bool:
        return bool(self.r2_account_id and self.r2_bucket and self.media_public_url)

    @property
    def database_path(self) -> Path:
        return self.data_dir / "studio.db"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"


settings = Settings()
