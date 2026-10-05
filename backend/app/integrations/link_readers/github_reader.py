"""
GitHub reader: details of a public repository from GitHub's public API
(no key needed): name, description, owner, start date, topics, and the
preview image GitHub makes for every repo.
"""

import re
from datetime import datetime

from app.integrations.link_readers.link_details import LinkDetails, LinkMedia, LinkReadError
from app.integrations.link_readers.web_fetch import fetch

_REPO_PATH = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")


def github_repo(url: str) -> tuple[str, str] | None:
    """(owner, repo) from a GitHub repository link, or None."""
    match = _REPO_PATH.search(url)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    return owner, repo


def read_github_repo(url: str) -> LinkDetails:
    found = github_repo(url)
    if not found:
        raise LinkReadError("That doesn't look like a GitHub repository link.")
    owner, repo = found

    response = fetch(f"https://api.github.com/repos/{owner}/{repo}")
    if response.status_code == 404:
        raise LinkReadError("GitHub can't find that repository. Is it public?")
    if response.status_code != 200:
        raise LinkReadError(f"GitHub didn't answer (status {response.status_code}). Try again later.")
    info = response.json()

    details = [info.get("description") or ""]
    if info.get("language"):
        details.append(f"Written in {info['language']}.")

    return LinkDetails(
        url=info.get("html_url", url),
        title=info.get("name", repo),
        description=" ".join(part for part in details if part),
        kind="project",
        author=info.get("owner", {}).get("login", owner),
        platform="GitHub",
        published_at=datetime.fromisoformat(info["created_at"]) if info.get("created_at") else None,
        media=[
            LinkMedia(
                type="image",
                url=f"https://opengraph.githubassets.com/1/{owner}/{repo}",
                thumbnail_url=f"https://opengraph.githubassets.com/1/{owner}/{repo}",
            )
        ],
    )
