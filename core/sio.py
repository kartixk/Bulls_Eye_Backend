from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flask_socketio import SocketIO

_sio: "SocketIO | None" = None


def set_sio(s: "SocketIO") -> None:
    global _sio
    _sio = s


def get_sio() -> "SocketIO | None":
    return _sio
