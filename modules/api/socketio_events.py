"""SocketIO event handlers — watchlist subscribe/unsubscribe for live ticks."""
from __future__ import annotations

import logging
from flask_socketio import SocketIO, emit, join_room, leave_room

log = logging.getLogger(__name__)


def register_socketio_handlers(sio: SocketIO) -> None:
    @sio.on("connect")
    def _connect():
        log.info("socket connected")
        emit("connected", {"ok": True})

    @sio.on("watchlist:subscribe")
    def _sub(data):
        for sym in data.get("symbols", []):
            join_room(f"sym:{sym}")

    @sio.on("watchlist:unsubscribe")
    def _unsub(data):
        for sym in data.get("symbols", []):
            leave_room(f"sym:{sym}")
