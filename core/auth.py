"""Internal API key validation helper."""
from __future__ import annotations

from functools import wraps

from flask import jsonify, request

from core.config import settings


def require_internal_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if (
            settings.INTERNAL_API_KEY
            and request.headers.get("X-Internal-Key") != settings.INTERNAL_API_KEY
        ):
            return jsonify(error="Unauthorized"), 401
        return f(*args, **kwargs)
    return decorated
