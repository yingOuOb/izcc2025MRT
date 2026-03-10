"""
Tests for the public REST API endpoints (Blueprint ``api``).

All tests use the ``TestConfig`` which bypasses Discord OAuth by reading
``session["test_user"]`` instead of calling the Discord API.
"""

import json
import pytest

from app.core import core
from app.game_config import ADMINS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_session(client, username, uid="1", avatar_url=""):
    with client.session_transaction() as sess:
        sess["test_user"] = {"username": username, "id": uid, "avatar_url": avatar_url}


def _admin_username():
    return ADMINS[0] if ADMINS else None


def _team_admin_username():
    for team in core.teams.values():
        if team.admins:
            return team.admins[0]
    return None


def _team_name_with_admin():
    for name, team in core.teams.items():
        if team.admins:
            return name
    return None


# ---------------------------------------------------------------------------
# /api/status_codes
# ---------------------------------------------------------------------------

class TestStatusCodes:

    def test_default_language(self, client):
        resp = client.get("/api/status_codes")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, dict)

    def test_specific_language(self, client):
        resp = client.get("/api/status_codes/en")
        assert resp.status_code == 200

    def test_unknown_language_returns_404(self, client):
        resp = client.get("/api/status_codes/zzz_UNKNOWN")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# /api/graph – requires is_player()
# ---------------------------------------------------------------------------

class TestGraph:

    def test_unauthenticated_returns_403(self, client):
        resp = client.get("/api/graph")
        assert resp.status_code == 403

    def test_game_admin_can_access(self, app):
        admin = _admin_username()
        if not admin:
            pytest.skip("No admins configured")
        c = app.test_client()
        _set_session(c, admin)
        resp = c.get("/api/graph")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, dict)

    def test_team_admin_can_access(self, app):
        username = _team_admin_username()
        if not username:
            pytest.skip("No team admins found")
        c = app.test_client()
        _set_session(c, username)
        resp = c.get("/api/graph")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /api/teams – requires is_player()
# ---------------------------------------------------------------------------

class TestTeams:

    def test_unauthenticated_returns_403(self, client):
        resp = client.get("/api/teams")
        assert resp.status_code == 403

    def test_game_admin_gets_team_list(self, app):
        admin = _admin_username()
        if not admin:
            pytest.skip("No admins configured")
        c = app.test_client()
        _set_session(c, admin)
        resp = c.get("/api/teams")
        assert resp.status_code == 200
        teams = json.loads(resp.data)
        assert isinstance(teams, list)


# ---------------------------------------------------------------------------
# /api/team/<name>
# ---------------------------------------------------------------------------

class TestTeamEndpoint:

    def test_existing_team_returns_data(self, app):
        admin = _admin_username()
        if not admin:
            pytest.skip("No admins configured")
        team_name = _team_name_with_admin()
        if not team_name:
            pytest.skip("No teams found")
        c = app.test_client()
        _set_session(c, admin)
        resp = c.get(f"/api/team/{team_name}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("name") == team_name

    def test_nonexistent_team_returns_empty(self, app):
        admin = _admin_username()
        if not admin:
            pytest.skip("No admins configured")
        c = app.test_client()
        _set_session(c, admin)
        resp = c.get("/api/team/no_such_team_xyz")
        assert resp.status_code == 200
        assert json.loads(resp.data) == {}


# ---------------------------------------------------------------------------
# /api/collapse_status and /api/next_collapse_time
# ---------------------------------------------------------------------------

class TestCollapseEndpoints:

    def test_collapse_status_requires_auth(self, client):
        resp = client.get("/api/collapse_status")
        assert resp.status_code == 403

    def test_next_collapse_time_requires_auth(self, client):
        resp = client.get("/api/next_collapse_time")
        assert resp.status_code == 403

    def test_collapse_status_accessible_by_admin(self, app):
        admin = _admin_username()
        if not admin:
            pytest.skip("No admins configured")
        c = app.test_client()
        _set_session(c, admin)
        resp = c.get("/api/collapse_status")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /api/users – requires is_admin()
# ---------------------------------------------------------------------------

class TestUsersEndpoint:

    def test_unauthenticated_returns_403(self, client):
        resp = client.get("/api/users")
        assert resp.status_code == 403

    def test_team_admin_can_access(self, app):
        username = _team_admin_username()
        if not username:
            pytest.skip("No team admins found")
        c = app.test_client()
        _set_session(c, username)
        resp = c.get("/api/users")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# /api/join_team – requires is_admin() + game running
# ---------------------------------------------------------------------------

class TestJoinTeam:

    def test_unauthenticated_returns_403(self, client):
        resp = client.get("/api/join_team/some_team/some_player")
        assert resp.status_code == 403

    def test_nonexistent_team_returns_status_code(self, app):
        username = _team_admin_username()
        if not username:
            pytest.skip("No team admins found")
        c = app.test_client()
        _set_session(c, username)
        resp = c.get("/api/join_team/no_such_team_xyz/player1")
        # Should return a valid response (not 403 / 500) for a missing team
        assert resp.status_code == 200
        # The response contains a localized "team not found" message (S00004)
        assert len(resp.data) > 0


# ---------------------------------------------------------------------------
# Redirect behaviour for unauthenticated requests to HTML pages
# ---------------------------------------------------------------------------

class TestMainRouteRedirects:

    def test_index_redirects_to_login_when_unauthenticated(self, client):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_login_redirects_to_oauth(self, client):
        resp = client.get("/login")
        # Should redirect (to Discord OAuth URL or back to / if not configured)
        assert resp.status_code == 302
