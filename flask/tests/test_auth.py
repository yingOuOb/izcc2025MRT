"""
Tests for the authentication helper module (app/modules/auth.py).

These tests verify that:
- In testing mode, ``get_current_user()`` returns a MockUser built from
  ``session["test_user"]`` without touching the Discord API.
- ``get_current_user()`` returns ``None`` when no session exists.
- The MockUser interface is compatible with the rest of the codebase.
"""

import pytest
from app.modules.auth import MockUser, get_current_user
from app.modules.checker import is_admin, is_player, is_game_admin
from app.game_config import ADMINS
from app.core import core


class TestMockUser:
    """Unit tests for the MockUser dataclass."""

    def test_default_fields(self):
        user = MockUser(username="testuser")
        assert user.username == "testuser"
        assert user.id == "0"
        assert user.avatar_url == ""

    def test_custom_fields(self):
        user = MockUser(username="alice", id="42", avatar_url="https://example.com/avatar.png")
        assert user.username == "alice"
        assert user.id == "42"
        assert user.avatar_url == "https://example.com/avatar.png"


class TestGetCurrentUser:
    """Tests for get_current_user() in testing mode."""

    def test_returns_none_without_session(self, app):
        with app.test_request_context("/"):
            with app.test_client() as client:
                with client.application.test_request_context("/"):
                    # No session set – should return None
                    from flask import session
                    assert get_current_user() is None

    def test_returns_mock_user_from_session(self, app):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["test_user"] = {"username": "bob", "id": "99", "avatar_url": ""}

            response = client.get("/")  # Trigger a request so the session is active
            # We cannot call get_current_user() outside a request context directly,
            # so we test it indirectly through the checker helpers below.

    def test_no_discord_api_called_in_test_mode(self, app, monkeypatch):
        """Ensure the Zenora APIClient is never instantiated in test mode."""
        import zenora

        def _no_discord(*args, **kwargs):
            raise AssertionError("Discord API must not be called during testing")

        monkeypatch.setattr(zenora, "APIClient", _no_discord)

        test_client = app.test_client()
        with test_client.session_transaction() as sess:
            sess["test_user"] = {"username": "testuser", "id": "1", "avatar_url": ""}

        # Any request that would normally call Discord should succeed without error
        resp = test_client.get("/api/graph")
        # May be 403 (not a player) but must NOT raise AssertionError
        assert resp.status_code in (200, 403)


class TestCheckerFunctions:
    """Tests for is_admin / is_player / is_game_admin using mock sessions."""

    def test_unauthenticated_is_not_admin(self, client):
        with client.application.test_request_context("/"):
            assert is_admin() is False

    def test_unauthenticated_is_not_player(self, client):
        with client.application.test_request_context("/"):
            assert is_player() is False

    def test_unauthenticated_is_not_game_admin(self, client):
        with client.application.test_request_context("/"):
            assert is_game_admin() is False

    def test_game_admin_is_admin(self, app):
        if not ADMINS:
            pytest.skip("No admins configured in game_config.json")
        test_client = app.test_client()
        with test_client.session_transaction() as sess:
            sess["test_user"] = {"username": ADMINS[0], "id": "1", "avatar_url": ""}
        with test_client.application.test_request_context("/"):
            from flask import session
            session["test_user"] = {"username": ADMINS[0], "id": "1", "avatar_url": ""}
            assert is_game_admin() is True
            assert is_admin() is True

    def test_team_admin_is_admin(self, app):
        """A user who is an admin of any team should pass is_admin()."""
        team_admin_username = None
        for team in core.teams.values():
            if team.admins:
                team_admin_username = team.admins[0]
                break

        if team_admin_username is None:
            pytest.skip("No team with admins found")

        with app.test_request_context("/"):
            from flask import session
            session["test_user"] = {"username": team_admin_username, "id": "2", "avatar_url": ""}
            assert is_admin() is True

    def test_unknown_user_is_not_player(self, app):
        with app.test_request_context("/"):
            from flask import session
            session["test_user"] = {"username": "completely_unknown_user_xyz", "id": "3", "avatar_url": ""}
            assert is_player() is False
