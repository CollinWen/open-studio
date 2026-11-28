"""
Add-on connections: linking a Composio add-on to the account it acts as,
without the owner handling a key. The studio asks Composio for a Connect
Link for the add-on's toolkit; the owner signs in on Composio's own page
(OAuth, or an API key typed there) and is sent back to the studio's
add-ons page with the new account's id, which the studio checks with
Composio (the studio's own Composio user, this toolkit, active) before
keeping it.

Used by addons/routes.py. Composio itself: integrations/composio_client.py.
"""

from urllib.parse import urlsplit

from sqlmodel import Session

from app.config import settings
from app.features.addons import service as addons_service
from app.features.addons.models import Addon
from app.integrations import composio_client
from app.integrations.composio_client import ComposioError


class ConnectionNotAllowedError(Exception):
    """This add-on can't be connected that way, or the account doesn't fit it."""


class ConnectionUnavailableError(Exception):
    """Composio isn't set up or couldn't be reached."""


def start_connection(addon: Addon, return_url: str) -> str:
    """The address of Composio's sign-in page for this add-on, which comes back to return_url."""
    if addon.kind != "composio":
        raise ConnectionNotAllowedError("Only Composio add-ons connect to an account")
    if not _is_studio_page(return_url):
        raise ConnectionNotAllowedError("Composio may only send you back to the studio's own pages")
    try:
        return composio_client.create_connect_link(settings.composio_user_id, addon.service, return_url)
    except ComposioError as error:
        raise ConnectionUnavailableError(str(error)) from error


def save_connection(db: Session, addon: Addon, connected_account_id: str) -> Addon:
    """Keep the account this add-on came back with, once Composio confirms it's the right one."""
    try:
        account = composio_client.get_connected_account(connected_account_id)
    except ComposioError as error:
        raise ConnectionUnavailableError(str(error)) from error
    toolkit = (account.get("toolkit") or {}).get("slug")
    if account.get("user_id") != settings.composio_user_id or toolkit != addon.service:
        raise ConnectionNotAllowedError(f"That isn't a {addon.service} account of the studio's Composio user")
    if account.get("status") != "ACTIVE":
        raise ConnectionNotAllowedError("That account isn't active: finish signing in on Composio's page")
    return addons_service.set_account(db, addon, connected_account_id)


def _is_studio_page(url: str) -> bool:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}" in settings.frontend_origins
