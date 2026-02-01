import logging
from flask_socketio import SocketIO

from ..core import core


log = logging.getLogger(__name__)
socketio = SocketIO(async_mode="gevent", async_handlers=False, cors_allowed_origins="*")


@socketio.on("Connect")
def connect(data):
    log.info(data["message"])
    socketio.emit("Connected", {"message": "Connected from server"})