"""
Settings: every value the backend reads from the environment, in one place.

Values come from backend/.env (see .env.example) or the shell. Nothing else
in the backend reads environment variables directly.
"""

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
# This repository's own skills folder: where skills are read from when AGENT_RESOURCES is empty.
REPO_SKILLS_DIR = BACKEND_DIR.parent / "skills"


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

    # How many entries one agent may add or edit per hour. Each write costs an LLM call.
    agent_writes_per_hour: int = int(os.environ.get("AGENT_WRITES_PER_HOUR", "60"))
    # How many lines one agent may write to the agent log per hour (plans, thoughts, findings).
    agent_log_lines_per_hour: int = int(os.environ.get("AGENT_LOG_LINES_PER_HOUR", "120"))
    # How many toolkit tools one agent may call per hour (features/toolkits/): each may cost a
    # paid API call (an Exa search, say) on one of your accounts.
    agent_toolkit_calls_per_hour: int = int(os.environ.get("AGENT_TOOLKIT_CALLS_PER_HOUR", "200"))

    # Runs: every token an agent works with is a run (features/runs/): one session, with
    # what it may do written into it. Tokens are signed with RUN_TOKEN_SECRET; left empty, a
    # secret is made from OWNER_TOKEN, so changing the password also ends every run.
    run_token_secret_setting: str = os.environ.get("RUN_TOKEN_SECRET", "")
    # How long a run's token works unless asked otherwise (4 hours), and the most it may be
    # given (90 days), in minutes.
    run_minutes: int = int(os.environ.get("RUN_MINUTES", str(4 * 60)))
    run_minutes_max: int = int(os.environ.get("RUN_MINUTES_MAX", str(90 * 24 * 60)))
    # Sites a run's session link may go to (the harness's own page for the session), comma
    # separated. A site also covers its subdomains. Empty: any web address.
    session_link_sites: tuple[str, ...] = tuple(
        site.strip().lower()
        for site in os.environ.get("SESSION_LINK_SITES", "claude.ai").split(",")
        if site.strip()
    )
    # This API's public address, put in each run's kit so the agent knows where to connect
    # (e.g. https://api.yourdomain.com). Empty: the address the request came in on.
    public_api_url: str = os.environ.get("PUBLIC_API_URL", "")

    # Agent resources: where the skills agents can be given are read from (features/skills/),
    # comma separated, first source winning when two hold the same skill. Each is a folder
    # on this machine, or a folder in a public GitHub repository at a branch, tag or commit:
    # "github:owner/repo@ref/path" (e.g. github:CollinWen/open-studio@main/skills).
    # Empty: this repository's own skills/ folder, when it's there (local development).
    agent_resources: tuple[str, ...] = tuple(
        source.strip() for source in os.environ.get("AGENT_RESOURCES", "").split(",") if source.strip()
    ) or ((str(REPO_SKILLS_DIR),) if REPO_SKILLS_DIR.is_dir() else ())
    # How long the skills read from those sources are kept before they're read again.
    agent_resources_cache_minutes: int = int(os.environ.get("AGENT_RESOURCES_CACHE_MINUTES", "10"))

    # Composio (integrations/composio_client.py): runs the tools of outside services (GitHub, Exa,
    # ...) for agents, as accounts you connected in Composio. The key stays here: agents call
    # through the studio (features/toolkits/), which checks each call against the run first.
    # Leave the key empty to turn toolkits off.
    composio_api_key: str = os.environ.get("COMPOSIO_API_KEY", "")
    # The Composio user your connected accounts belong to (one for the whole studio).
    composio_user_id: str = os.environ.get("COMPOSIO_USER_ID", "open-studio")
    composio_base_url: str = os.environ.get("COMPOSIO_BASE_URL", "https://backend.composio.dev")

    # OpenRouter: one key covers both the tag model and the embedding model.
    openrouter_api_key: str = os.environ.get("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    tag_model: str = os.environ.get("TAG_MODEL", "z-ai/glm-5.3-flash")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    # A model that can look at pictures, used to describe each picture in words before embedding.
    picture_model: str = os.environ.get("PICTURE_MODEL", "google/gemini-2.5-flash-lite")
    # Read entries (pictures, source link, tags, embedding) after saving, without making the save wait.
    # Off in tests, so the reading happens before the request returns.
    read_in_background: bool = os.environ.get("READ_IN_BACKGROUND", "true").lower() != "false"
    # How many of an entry's pictures are read, and the largest stored file sent to be read.
    pictures_read_per_entry: int = int(os.environ.get("PICTURES_READ_PER_ENTRY", 8))
    picture_max_bytes_for_reading: int = int(os.environ.get("PICTURE_MAX_BYTES_FOR_READING", 8_000_000))
    # How much of a source link's own text (a video's description, a post's caption) is kept.
    source_text_for_meaning: int = int(os.environ.get("SOURCE_TEXT_FOR_MEANING", 3000))

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
    # The largest write-up (HTML, embedded pictures included) the studio will store.
    writeup_max_bytes: int = int(os.environ.get("WRITEUP_MAX_BYTES", 5_000_000))
    # How much of an entry's write-up text goes into its tags and embedding (the start of it).
    writeup_text_for_meaning: int = int(os.environ.get("WRITEUP_TEXT_FOR_MEANING", 6000))

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    @property
    def run_token_secret(self) -> bytes:
        """The key run tokens are signed with; empty when there is neither setting."""
        if self.run_token_secret_setting:
            return self.run_token_secret_setting.encode()
        if self.owner_token:
            return hashlib.sha256(f"open-studio run tokens:{self.owner_token}".encode()).digest()
        return b""

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
