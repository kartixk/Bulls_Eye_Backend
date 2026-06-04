"""Flask app factory + SocketIO init + scheduler startup."""
from __future__ import annotations

import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from core.config import settings
from core.logger import configure_logging
from core.sio import set_sio
from modules.api.routes import api_bp
from modules.api.socketio_events import register_socketio_handlers
from modules.scheduler.scheduler import start_scheduler

configure_logging()
log = logging.getLogger(__name__)


def create_app() -> tuple[Flask, SocketIO]:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY
    cors_origins = settings.CORS_ORIGINS.split(",")
    CORS(app, resources={r"/*": {"origins": cors_origins}})
    app.register_blueprint(api_bp)

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok")

    socketio = SocketIO(app, cors_allowed_origins=cors_origins, async_mode="eventlet")
    set_sio(socketio)
    register_socketio_handlers(socketio)
    start_scheduler(socketio)
    log.info("App initialised")
    return app, socketio


app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
