"""
Add-on service: the owner defining, changing and removing add-ons (each
starts with a guide written from its kind's template) and looking through a
Composio add-on's tools, the three built-in ones every studio has (web,
code and github: the sandbox's own tools), and checking the add-on names
an agent is given.

Used by addons/routes.py, addons/connections.py (keeping an add-on's
account), agents/service.py (checking names) and runs/service.py (a run's
add-ons, for its sandbox). Agents calling an add-on's tools: relay.py.
"""

from sqlmodel import Session, select

from app.features.addons.guide_templates import write_default_guide
from app.features.addons.models import Addon
from app.features.addons.schemas import SANDBOX_SERVICES, AddonCreate, AddonOut, CatalogTool
from app.integrations import composio_client
from app.integrations.composio_client import ComposioError

# The sandbox's own tools, as add-ons every studio has from the start.
BUILT_IN = SANDBOX_SERVICES


class AddonExistsError(Exception):
    """An add-on with this name is already there."""


class AddonNotAllowedError(Exception):
    """Not something this add-on allows (removing a built-in one, a sandbox one's catalog)."""


class CatalogUnavailableError(Exception):
    """Composio isn't set up or couldn't be reached."""


class UnknownAddonsError(Exception):
    def __init__(self, names: list[str]):
        self.names = names
        super().__init__(f"No such add-ons: {', '.join(names)} (the studio's add-ons page lists them)")


def list_addons(db: Session) -> list[Addon]:
    """Built-in ones first, then by name."""
    addons = db.exec(select(Addon)).all()
    return sorted(addons, key=lambda addon: (addon.name not in BUILT_IN, addon.name))


def get_addon(db: Session, name: str) -> Addon | None:
    return db.get(Addon, name)


def find_addons(db: Session, names: list[str]) -> list[Addon]:
    """These add-ons in this order, leaving out any since removed."""
    found = (db.get(Addon, name) for name in dict.fromkeys(names))
    return [addon for addon in found if addon is not None]


def check_addon_names(db: Session, names: list[str]) -> None:
    unknown = [name for name in dict.fromkeys(names) if db.get(Addon, name) is None]
    if unknown:
        raise UnknownAddonsError(unknown)


def describe_addon(addon: Addon) -> AddonOut:
    return AddonOut(**addon.model_dump(), built_in=addon.name in BUILT_IN)


def create_addon(db: Session, data: AddonCreate) -> Addon:
    if db.get(Addon, data.name) is not None:
        raise AddonExistsError(f"Add-on {data.name} already exists")
    guide = data.guide if data.guide is not None else write_default_guide(data.kind, data.service)
    addon = Addon(name=data.name, kind=data.kind, service=data.service, guide=guide)
    return _save(db, addon)


def update_guide(db: Session, addon: Addon, guide: str) -> Addon:
    addon.guide = guide
    return _save(db, addon)


def set_account(db: Session, addon: Addon, account: str) -> Addon:
    addon.account = account
    return _save(db, addon)


def remove_addon(db: Session, addon: Addon) -> None:
    """Agents that had it keep its name, shown as gone, and their runs go on without it."""
    if addon.name in BUILT_IN:
        raise AddonNotAllowedError("Built-in add-ons stay: take them off agents instead")
    db.delete(addon)
    db.commit()


def list_catalog(addon: Addon, query: str = "") -> list[CatalogTool]:
    """Every tool of a Composio add-on's toolkit, with Composio's hint of what each does."""
    if addon.kind != "composio":
        raise AddonNotAllowedError("Only Composio add-ons have a catalog of tools")
    try:
        items = composio_client.list_toolkit_tools(addon.service, query)
    except ComposioError as error:
        raise CatalogUnavailableError(str(error)) from error
    return [
        CatalogTool(tool=item["slug"], name=item.get("name", ""), description=item.get("description", ""), tags=item.get("tags") or [])
        for item in items
    ]


def ensure_builtin_addons(db: Session) -> None:
    """Make web, code and github if they're missing (on startup)."""
    for service in BUILT_IN:
        if db.get(Addon, service) is None:
            db.add(Addon(name=service, kind="sandbox", service=service, guide=write_default_guide("sandbox", service)))
    db.commit()


def _save(db: Session, addon: Addon) -> Addon:
    db.add(addon)
    db.commit()
    db.refresh(addon)
    return addon
