"""
Shared pytest fixtures for the test suite.

All tests run against a TestConfig-based Flask app that:
- Uses an in-memory SQLite database (no leftover state between test runs).
- Has CSRF protection disabled so API calls don't need CSRF tokens.
- Replaces Discord OAuth with a simple session key ``test_user`` so tests
  can simulate different user roles without a live Discord connection.
"""

import pytest

from app import create_app
from app.config import TestConfig
from app.game_config import ADMINS


@pytest.fixture(scope="session")
def app():
    """Create a single Flask application instance for the whole test session."""
    application = create_app(TestConfig)
    yield application


@pytest.fixture
def client(app):
    """Unauthenticated test client."""
    return app.test_client()


@pytest.fixture
def game_admin_client(app):
    """Test client authenticated as a game admin (in the ADMINS list)."""
    admin_username = ADMINS[0] if ADMINS else "test_game_admin"
    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["test_user"] = {
            "username": admin_username,
            "id": "111111111",
            "avatar_url": "",
        }
    return test_client


@pytest.fixture
def team_admin_client(app):
    """Test client authenticated as a team admin (member of the admins list of a team)."""
    from app.core import core

    # Pick the first team that has at least one admin configured
    team_admin_username = None
    for team in core.teams.values():
        if team.admins:
            team_admin_username = team.admins[0]
            break

    if team_admin_username is None:
        pytest.skip("No team with admins found in presets")

    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["test_user"] = {
            "username": team_admin_username,
            "id": "222222222",
            "avatar_url": "",
        }
    return test_client


@pytest.fixture
def player_client(app):
    """Test client authenticated as a regular player (in a team's players list)."""
    from app.core import core

    player_username = None
    for team in core.teams.values():
        if team.players:
            player_username = team.players[0]
            break

    if player_username is None:
        pytest.skip("No teams with players found in presets")

    test_client = app.test_client()
    with test_client.session_transaction() as sess:
        sess["test_user"] = {
            "username": player_username,
            "id": "333333333",
            "avatar_url": "",
        }
    return test_client
