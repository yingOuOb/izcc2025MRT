from flask import current_app, session

from ..game_config import ADMINS
from ..core import core
from .auth import get_current_user


def _is_logged_in() -> bool:
    """Return True if there is an active session (works in both test and production mode)."""
    if current_app.config.get("TESTING"):
        return "test_user" in session
    return "token" in session


def is_admin() -> bool:
    if not _is_logged_in():
        return False
    current_user = get_current_user()
    if current_user is None:
        return False
    _, output = core.check_player(current_user.username)
    return output or (current_user.username in ADMINS)


def is_player() -> bool:
    if not _is_logged_in():
        return False
    current_user = get_current_user()
    if current_user is None:
        return False
    output, _ = core.check_player(current_user.username)
    return (output is not None) or (current_user.username in ADMINS)


def is_game_admin() -> bool:
    if not _is_logged_in():
        return False
    current_user = get_current_user()
    if current_user is None:
        return False
    return current_user.username in ADMINS