"""
Tests for runs (every agent token is one): only the owner issues a token and
gets a kit (token, MCP address, prompt, command); a token reaches only its
boards, or all its agent's boards ("*"), and each call is checked against the
agent's boards too; it records the run on what it adds, can't edit or link
entries on other boards, logs only on its boards (a line that names none
lands on a one-board run's board), and stops working when the run is
finished, runs out or its agent is paused; it lasts 4 hours unless asked, at
most 90 days; a run can't be given outside tools the agent wasn't granted
(unless picked, it gets all it was granted); a run leaves a link to its harness's
session (a web address, while it's live, on an allowed site) that only the
owner and the run's agent see, and the log narrows to one run's lines.
"""

import uuid

from datetime import datetime, timezone

from conftest import AGENT_BOARD, OWNER_HEADERS, SCOUT_HEADERS, issue_token

NINETY_DAYS = 90 * 24 * 60


def _add_agent(client, tools: list[str] | None = None) -> tuple[str, dict]:
    """A new agent on AGENT_BOARD and "second", and a token for all its boards."""
    name = f"r-{uuid.uuid4().hex[:8]}"
    body = {"name": name, "boards": [AGENT_BOARD, "second"], "tools": tools or []}
    response = client.post("/api/agents", json=body, headers=OWNER_HEADERS)
    assert response.status_code == 200, response.text
    return name, issue_token(name)


def _start(client, agent: str, headers=OWNER_HEADERS, **fields):
    body = {"agent": agent, "boards": [AGENT_BOARD], **fields}
    return client.post("/api/runs", json=body, headers=headers)


def _bearer(kit: dict) -> dict:
    return {"Authorization": f"Bearer {kit['token']}"}


def _entry(board: str = AGENT_BOARD) -> dict:
    return {"board": board, "title": f"t {uuid.uuid4().hex}", "description": "why"}


def _second_board(client):
    client.post("/api/boards", json={"slug": "second", "name": "Second"}, headers=OWNER_HEADERS)


def test_the_owner_starts_a_run_and_gets_a_kit(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    response = _start(client, name)
    assert response.status_code == 200, response.text
    kit = response.json()
    assert kit["token"].startswith("run.")
    assert kit["mcp_url"] == kit["api_url"] + "/mcp"
    assert kit["run"]["scopes"] == [f"board:{AGENT_BOARD}", "web"]
    assert kit["run"]["boards"] == [AGENT_BOARD]
    assert kit["run"]["state"] == "running"
    assert "Your manifest" in kit["prompt"] and "studio-collaborator" in kit["prompt"]
    assert "WebFetch" in kit["setups"]["claude_code"]["allowed_tools"]
    assert kit["setups"]["claude_code"]["command"].startswith("claude -p ")


def test_a_run_adds_only_to_its_board_and_is_recorded(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    added = client.post("/api/entries", json=_entry(), headers=_bearer(kit))
    assert added.status_code == 200, added.text
    assert added.json()["added_by"] == f"agent:{name}"
    other_board = client.post("/api/entries", json=_entry("second"), headers=_bearer(kit))
    assert other_board.status_code == 403

    run = client.get(f"/api/runs/{kit['run']['id']}", headers=OWNER_HEADERS).json()
    assert run["added"] == [added.json()["id"]]


def test_finishing_a_run_ends_its_token(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    finished = client.post(f"/api/runs/{kit['run']['id']}/finish", json={"summary": "done"}, headers=_bearer(kit))
    assert finished.json()["state"] == "finished"
    assert finished.json()["summary"] == "done"
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 401


def test_pausing_the_agent_stops_its_runs(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    client.patch(f"/api/agents/{name}", json={"active": False}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 401


def test_a_run_gets_only_tools_the_agent_was_granted(client):
    name, _ = _add_agent(client, tools=["web"])
    refused = _start(client, name, tools=["web", "code"])
    assert refused.status_code == 403
    assert "code" in refused.json()["detail"]
    narrowed = _start(client, name, tools=["web"])
    assert narrowed.json()["run"]["tools"] == ["web"]


def test_a_token_lasts_four_hours_unless_asked_and_at_most_ninety_days(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    expires = datetime.fromisoformat(kit["run"]["expires_at"]).replace(tzinfo=timezone.utc)
    hours_left = (expires - datetime.now(timezone.utc)).total_seconds() / 3600
    assert 3.9 < hours_left <= 4
    assert _start(client, name, minutes=20).status_code == 200
    assert _start(client, name, minutes=NINETY_DAYS).status_code == 200
    assert _start(client, name, minutes=NINETY_DAYS + 1).status_code == 403


def test_only_the_owner_issues_tokens(client):
    name, headers = _add_agent(client, tools=["web"])
    assert _start(client, name, headers=headers).status_code == 401
    assert _start(client, name, headers=SCOUT_HEADERS).status_code == 401
    assert _start(client, name, headers={}).status_code == 401


def test_a_token_reaches_only_its_boards(client):
    _second_board(client)
    client.post("/api/boards", json={"slug": "third", "name": "Third"}, headers=OWNER_HEADERS)
    name, _ = _add_agent(client, tools=["web"])
    assert _start(client, name, boards=["third"]).status_code == 403
    kit = _start(client, name, boards=[AGENT_BOARD, "second"]).json()
    assert kit["run"]["scopes"] == [f"board:{AGENT_BOARD}", "board:second", "web"]
    assert f'get_board_brief("{AGENT_BOARD}"); get_board_brief("second")' in kit["prompt"]
    for board in (AGENT_BOARD, "second"):
        assert client.post("/api/entries", json=_entry(board), headers=_bearer(kit)).status_code == 200

    # Taken off a board, the agent can't reach it on a token that names it.
    client.patch(f"/api/agents/{name}", json={"boards": ["second"]}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 403


def test_a_token_for_all_boards_follows_the_agents_boards(client):
    _second_board(client)
    name, headers = _add_agent(client)
    assert client.post("/api/entries", json=_entry("second"), headers=headers).status_code == 200
    client.patch(f"/api/agents/{name}", json={"boards": [AGENT_BOARD]}, headers=OWNER_HEADERS)
    assert client.post("/api/entries", json=_entry("second"), headers=headers).status_code == 403
    assert client.post("/api/entries", json=_entry(), headers=headers).status_code == 200
    assert _start(client, name, boards=["*", AGENT_BOARD]).status_code == 403


def test_a_run_gets_every_tool_its_agent_was_granted_unless_narrowed(client):
    name, _ = _add_agent(client, tools=["web", "code"])
    kit = client.post("/api/runs", json={"agent": name, "boards": ["*"]}, headers=OWNER_HEADERS).json()
    assert kit["run"]["tools"] == ["web", "code"]
    assert "every board you're signed on to" in kit["prompt"]


def test_a_run_token_cannot_start_more_runs(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert _start(client, name, headers=_bearer(kit)).status_code == 401


def test_only_the_owner_lists_runs_and_others_cannot_see_one(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert client.get("/api/runs").status_code == 401
    assert client.get(f"/api/runs/{kit['run']['id']}", headers=SCOUT_HEADERS).status_code == 404
    listed = client.get("/api/runs", params={"agent": name}, headers=OWNER_HEADERS).json()
    assert listed[0]["id"] == kit["run"]["id"]  # newest first
    assert {run["agent"] for run in listed} == {name}



def _entries_on_two_boards(client) -> tuple[dict, dict, dict]:
    """A run on AGENT_BOARD, an agent entry on that board, and one on "second"."""
    _second_board(client)
    name, agent_headers = _add_agent(client, tools=["web"])
    mine = client.post("/api/entries", json=_entry(), headers=agent_headers).json()
    elsewhere = client.post("/api/entries", json=_entry("second"), headers=agent_headers).json()
    return _start(client, name).json(), mine, elsewhere


def test_a_run_cannot_edit_or_link_entries_on_other_boards(client):
    kit, mine, elsewhere = _entries_on_two_boards(client)
    edit = client.patch(f"/api/entries/{elsewhere['id']}", json={"title": "x"}, headers=_bearer(kit))
    assert edit.status_code == 403
    link = {"builds_on_id": mine["id"], "note": "n"}
    assert client.post(f"/api/entries/{elsewhere['id']}/builds-on", json=link, headers=_bearer(kit)).status_code == 403


def test_a_run_has_full_use_of_its_own_board(client):
    kit, mine, elsewhere = _entries_on_two_boards(client)
    assert client.patch(f"/api/entries/{mine['id']}", json={"title": "y"}, headers=_bearer(kit)).status_code == 200
    # Its entries may point at entries on other boards; only changing those is out of reach.
    back = {"builds_on_id": elsewhere["id"], "note": "n"}
    assert client.post(f"/api/entries/{mine['id']}/builds-on", json=back, headers=_bearer(kit)).status_code == 200
    assert client.get(f"/api/entries/{elsewhere['id']}", headers=_bearer(kit)).status_code == 200


def test_a_run_works_over_plain_http_without_any_harness(client):
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    run_path = f"/api/runs/{kit['run']['id']}"
    assert client.get(run_path, headers=_bearer(kit)).json()["boards"] == [AGENT_BOARD]
    assert client.get("/api/search", params={"q": "x"}, headers=_bearer(kit)).status_code == 200
    assert client.post("/api/entries", json=_entry(), headers=_bearer(kit)).status_code == 200
    line = {"board": AGENT_BOARD, "type": "finding", "text": "found it"}
    assert client.post("/api/agent-log", json=line, headers=_bearer(kit)).status_code == 200
    assert client.post(f"{run_path}/finish", json={"summary": "done"}, headers=_bearer(kit)).status_code == 200


def test_a_runs_log_lines_stay_on_its_board(client):
    _second_board(client)
    name, agent_headers = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    elsewhere = client.post("/api/entries", json=_entry("second"), headers=agent_headers).json()

    unnamed = client.post("/api/agent-log", json={"type": "status", "text": "starting"}, headers=_bearer(kit))
    assert unnamed.status_code == 200, unnamed.text
    assert unnamed.json()["board"] == AGENT_BOARD
    about_elsewhere = {"type": "finding", "text": "seen", "entry_id": elsewhere["id"]}
    assert client.post("/api/agent-log", json=about_elsewhere, headers=_bearer(kit)).status_code == 403


def test_the_log_narrows_to_one_runs_lines(client):
    _second_board(client)
    name, agent_headers = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    client.post("/api/agent-log", json={"type": "plan", "text": "on the run"}, headers=_bearer(kit))
    client.post("/api/agent-log", json={"board": AGENT_BOARD, "type": "plan", "text": "off it"}, headers=agent_headers)
    lines = client.get(f"/api/agent-log?run={kit['run']['id']}").json()
    assert [line["text"] for line in lines] == ["on the run"]


def test_a_run_leaves_its_session_link_for_the_owner(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert kit["run"]["session_url"] == ""
    assert "set_run_session" in kit["prompt"]
    link = "https://claude.ai/code/session_abc"
    response = client.post(f"/api/runs/{kit['run']['id']}/session", json={"url": f" {link} "}, headers=_bearer(kit))
    assert response.status_code == 200, response.text
    assert response.json()["session_url"] == link
    listed = client.get(f"/api/runs?agent={name}", headers=OWNER_HEADERS).json()
    assert listed[0]["session_url"] == link


def test_a_run_that_ran_out_takes_no_session_link(client):
    from datetime import datetime, timedelta, timezone

    from sqlmodel import Session

    from app.database import engine
    from app.features.runs.models import Run

    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    run_id = _start(client, name).json()["run"]["id"]
    with Session(engine) as db:
        run = db.get(Run, run_id)
        run.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.add(run)
        db.commit()
    late = client.post(f"/api/runs/{run_id}/session", json={"url": "https://claude.ai/code/s"}, headers=OWNER_HEADERS)
    assert late.status_code == 409


def test_a_session_link_must_be_a_web_address_and_the_run_live(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    run_id = kit["run"]["id"]
    bad = client.post(f"/api/runs/{run_id}/session", json={"url": "javascript:alert(1)"}, headers=_bearer(kit))
    assert bad.status_code == 422
    client.post(f"/api/runs/{run_id}/finish", json={"summary": "done"}, headers=OWNER_HEADERS)
    late = client.post(f"/api/runs/{run_id}/session", json={"url": "https://claude.ai/code/s"}, headers=OWNER_HEADERS)
    assert late.status_code == 409


def test_only_the_owner_or_the_runs_agent_sets_its_session(client):
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    response = client.post(f"/api/runs/{kit['run']['id']}/session", json={"url": "https://claude.ai/code/s"}, headers=SCOUT_HEADERS)
    assert response.status_code == 404


def _allow_session_sites(monkeypatch, *sites: str) -> None:
    from dataclasses import replace

    from app.features.runs import run_kit, service

    for module in (service, run_kit):
        monkeypatch.setattr(module, "settings", replace(module.settings, session_link_sites=sites))


def test_a_session_link_goes_only_to_an_allowed_site(client, monkeypatch):
    _allow_session_sites(monkeypatch, "claude.ai")
    _second_board(client)
    name, _ = _add_agent(client, tools=["web"])
    kit = _start(client, name).json()
    assert "(on claude.ai)" in kit["prompt"]
    url = f"/api/runs/{kit['run']['id']}/session"
    for elsewhere in ["https://claude.ai.example.com/s", "https://notclaude.ai/s", "https://example.com/claude.ai"]:
        assert client.post(url, json={"url": elsewhere}, headers=_bearer(kit)).status_code == 422, elsewhere
    assert client.post(url, json={"url": "https://code.claude.ai/s"}, headers=_bearer(kit)).status_code == 200

    _allow_session_sites(monkeypatch)
    assert client.post(url, json={"url": "https://example.com/s"}, headers=_bearer(kit)).status_code == 200
