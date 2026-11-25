"""
GitHub archive: one folder of a public GitHub repository at a branch, tag
or commit, as its files (path inside the folder, then bytes). Downloads the
repository's tarball from codeload.github.com, which needs no API key and
has no rate limit, and keeps only the files under the folder asked for.

Knows nothing about skills; features/skills/skill_sources.py uses it.
"""

import io
import ssl
import tarfile

import httpx
import truststore

ARCHIVE_URL = "https://codeload.github.com/{owner}/{repo}/tar.gz/{ref}"
TIMEOUT_SECONDS = 30
# A repository of skills is small; anything far bigger is the wrong address.
MAX_ARCHIVE_BYTES = 50_000_000
# Larger files in the folder (pictures, data) are left out.
MAX_FILE_BYTES = 1_000_000

# The operating system's certificates, as in openrouter_http.py.
_ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


class GithubArchiveError(Exception):
    """The archive couldn't be downloaded or read."""


def read_github_folder(owner: str, repo: str, ref: str, folder: str) -> dict[str, bytes]:
    """Every file under `folder` ("" for the whole repository) at `ref`."""
    url = ARCHIVE_URL.format(owner=owner, repo=repo, ref=ref)
    try:
        with httpx.Client(verify=_ssl_context, timeout=TIMEOUT_SECONDS, follow_redirects=True) as http:
            response = http.get(url)
    except httpx.HTTPError as error:
        raise GithubArchiveError(f"Couldn't reach GitHub for {owner}/{repo}@{ref}: {error}") from error
    if response.status_code != 200:
        raise GithubArchiveError(f"GitHub has no {owner}/{repo}@{ref} (answered {response.status_code})")
    if len(response.content) > MAX_ARCHIVE_BYTES:
        raise GithubArchiveError(f"{owner}/{repo}@{ref} is too large to read")
    return files_in_archive(response.content, folder)


def files_in_archive(archive: bytes, folder: str) -> dict[str, bytes]:
    """The regular files under `folder` in a GitHub tarball, by their path inside it.
    GitHub puts everything under one top folder (repo-ref/), which is skipped."""
    folder = folder.strip("/")
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile() or member.size > MAX_FILE_BYTES:
                    continue
                path = "/".join(member.name.split("/")[1:])
                if folder:
                    if not path.startswith(f"{folder}/"):
                        continue
                    path = path[len(folder) + 1 :]
                if not path or ".." in path.split("/"):
                    continue
                extracted = tar.extractfile(member)
                if extracted is not None:
                    files[path] = extracted.read()
    except (tarfile.TarError, OSError) as error:
        raise GithubArchiveError(f"Couldn't read the archive: {error}") from error
    return files
