"""
Tests for defining add-ons (the owner's side), with a stand-in for
Composio: web, code and github are there from the start and stay; a new
add-on's guide starts from its kind's template; a sandbox add-on's service
must be one of the sandbox's own tools; only the owner sees or changes
add-ons; an agent is given add-ons by name, with instructions kept only
for the ones it has and shown only to the owner; the AGENTS.md preview
holds each add-on's guide and the owner's instructions; a removed add-on
leaves agents and runs without it; a Composio add-on shows its toolkit's
tools, and connects through Composio's sign-in page, keeping the account
only once Composio confirms it fits.
"""

import uuid

import pytest

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS

from app.integrations import composio_client

STUDIO_PAGE = "http://localhost:5173/studio/addons"


def _addon(client, service="gmail", **fields) -> str:
    name = f"a-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "kind": "composio", "service": service, **fields}
    response = client.post("/api/addons", json=body, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    return name


@pytest.fixture
def composio(monkeypatch):
    """A stand-in Composio for the catalog and connecting."""
    accounts = {
        "ca_mail": {"id": "ca_mail", "status": "ACTIVE", "user_id": "open-studio", "toolkit": {"slug": "gmail"}},
        "ca_other_user": {"id": "ca_other_user", "status": "ACTIVE", "user_id": "someone", "toolkit": {"slug": "gmail"}},
        "ca_pending": {"id": "ca_pending", "status": "INITIATED", "user_id": "open-studio", "toolkit": {"slug": "gmail"}},
    }
    monkeypatch.setattr(composio_client, "list_toolkit_tools", lambda toolkit, query="": [
        {"slug": "GMAIL_FETCH_EMAILS", "name": "Fetch emails", "description": "Read mail", "tags": ["readOnlyHint"]},
    ])
    monkeypatch.setattr(composio_client, "create_connect_link", lambda user, toolkit, back: f"https://connect.test/{toolkit}?back={back}")
    monkeypatch.setattr(composio_client, "get_connected_account", lambda account: accounts[account])


def test_the_built_in_add_ons_are_there_and_stay(client):
    listed = {addon["name"]: addon for addon in client.get("/api/addons", headers=OWNER_HEADERS).json()}
    assert {"web", "code", "github"} <= set(listed)
    assert listed["code"]["kind"] == "sandbox" and listed["code"]["built_in"]
    assert listed["code"]["guide"].startswith("**What it is:** a shell")
    assert client.delete("/api/addons/code", headers=OWNER_HEADERS).status_code == 409
    assert client.get("/api/addons").status_code == 401
    assert client.get("/api/addons", headers=SCOUT_HEADERS).status_code == 401


def test_a_new_add_ons_guide_starts_from_its_template(client):
    name = _addon(client)
    addon = next(one for one in client.get("/api/addons", headers=OWNER_HEADERS).json() if one["name"] == name)
    assert "reading, searching and drafting email" in addon["guide"] and "call_addon_tool" in addon["guide"]
    assert addon["account"] == "" and not addon["built_in"]
    changed = client.patch(f"/api/addons/{name}", json={"guide": "Mail, as the studio's assistant."}, headers=OWNER_HEADERS)
    assert changed.json()["guide"] == "Mail, as the studio's assistant."
    assert _addon(client, guide="My own words.")
    bad = {"name": "x-shell", "kind": "sandbox", "service": "shell"}
    assert client.post("/api/addons", json=bad, headers=OWNER_HEADERS).status_code == 422
    assert client.post("/api/addons", json={"name": name, "kind": "composio", "service": "exa"}, headers=OWNER_HEADERS).status_code == 409


def test_an_agent_gets_add_ons_by_name_with_its_own_instructions(client):
    mail = _addon(client)
    name = f"g-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD], "addons": ["web", mail],
            "addon_instructions": {mail: "Draft replies; never send.", "code": "dropped: not one of its add-ons"}}
    agent = client.post("/api/agents", json=body, headers=OWNER_HEADERS).json()
    assert agent["addons"] == ["web", mail]
    assert agent["addon_instructions"] == {mail: "Draft replies; never send."}
    assert client.get(f"/api/agents/{name}").json()["addon_instructions"] == {}
    unknown = client.patch(f"/api/agents/{name}", json={"addons": ["no-such-addon"]}, headers=OWNER_HEADERS)
    assert unknown.status_code == 422 and "no-such-addon" in unknown.json()["detail"]

    preview = client.get(f"/api/agents/{name}/agents-md", headers=OWNER_HEADERS)
    assert preview.status_code == 200 and client.get(f"/api/agents/{name}/agents-md").status_code == 401
    text = preview.text
    assert f"### {mail}" in text and "Not connected yet" in text and "Draft replies; never send." in text
    assert "### web" in text and f"You may add to and log on: {AGENT_BOARD}." in text


def test_a_removed_add_on_leaves_agents_and_runs_without_it(client):
    mail = _addon(client)
    name = f"g-{uuid.uuid4().hex[:8]}"
    client.post("/api/agents", json={"name": name, "boards": [AGENT_BOARD], "addons": ["web", mail]}, headers=OWNER_HEADERS)
    assert client.delete(f"/api/addons/{mail}", headers=OWNER_HEADERS).status_code == 204
    assert client.get(f"/api/agents/{name}", headers=OWNER_HEADERS).json()["addons"] == ["web", mail]
    kit = client.post("/api/runs", json={"agent": name, "boards": ["*"]}, headers=OWNER_HEADERS).json()
    assert kit["run"]["addons"] == ["web"]


def test_a_composio_add_on_shows_its_tools_and_connects_through_composio(client, composio):
    mail = _addon(client)
    catalog = client.get(f"/api/addons/{mail}/catalog", headers=OWNER_HEADERS).json()
    assert catalog == [{"tool": "GMAIL_FETCH_EMAILS", "name": "Fetch emails", "description": "Read mail", "tags": ["readOnlyHint"]}]
    assert client.get("/api/addons/web/catalog", headers=OWNER_HEADERS).status_code == 400

    link = client.post(f"/api/addons/{mail}/connect", json={"return_url": STUDIO_PAGE}, headers=OWNER_HEADERS)
    assert link.json()["url"] == f"https://connect.test/gmail?back={STUDIO_PAGE}"
    elsewhere = client.post(f"/api/addons/{mail}/connect", json={"return_url": "https://evil.test/"}, headers=OWNER_HEADERS)
    assert elsewhere.status_code == 400

    for wrong in ("ca_other_user", "ca_pending"):
        refused = client.post(f"/api/addons/{mail}/connection", json={"connected_account_id": wrong}, headers=OWNER_HEADERS)
        assert refused.status_code == 400, wrong
    kept = client.post(f"/api/addons/{mail}/connection", json={"connected_account_id": "ca_mail"}, headers=OWNER_HEADERS)
    assert kept.status_code == 200 and kept.json()["account"] == "ca_mail"
