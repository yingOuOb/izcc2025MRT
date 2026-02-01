import logging
from flask_socketio import SocketIO

from ..core import core


log = logging.getLogger(__name__)
socketio = SocketIO(async_mode="gevent_uwsgi", async_handlers=False)


@socketio.on("Connect")
def connect(data):
    log.info(data["message"])
    socketio.emit("Connected", {"message": "Connected from server"})