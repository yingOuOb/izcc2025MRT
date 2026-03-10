import logging
from flask import session, current_app
from zenora import APIClient


log = logging.getLogger(__name__)


class MockUser:
    """
    Mock Discord user for testing purposes.
    
    Provides the same interface as the Zenora Discord user object
    so existing code works unchanged in test mode.
    """
    
    def __init__(self, username: str, id: str = "0", avatar_url: str = ""):
        self.username = username
        self.id = id
        self.avatar_url = avatar_url


def get_current_user():
    """
    Get the currently authenticated user.
    
    In testing mode (``TESTING=True`` in app config), returns a
    :class:`MockUser` constructed from ``session["test_user"]`` so that
    unit tests can inject arbitrary user identities without a live
    Discord connection.
    
    In production mode the standard Discord OAuth bearer token stored
    in ``session["token"]`` is used to call the Discord API via Zenora.
    
    Returns
    -------
    user : :class:`MockUser` | Zenora user object | ``None``
        The authenticated user, or ``None`` if no session exists.
    """
    
    if current_app.config.get("TESTING"):
        test_user = session.get("test_user")
        if test_user is None:
            return None
        return MockUser(
            username=test_user.get("username", ""),
            id=test_user.get("id", "0"),
            avatar_url=test_user.get("avatar_url", ""),
        )
    
    token = session.get("token")
    if token is None:
        return None
    
    bearer_client = APIClient(token, bearer=True)
    return bearer_client.users.get_current_user()
