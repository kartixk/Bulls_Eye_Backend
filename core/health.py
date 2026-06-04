from __future__ import annotations
import logging
from core.db import get_db

log = logging.getLogger(__name__)


def log_health_event(component: str, status: str, message: str = "") -> None:
    """Write a row to public.system_health. Fire-and-forget — never raises."""
    try:
        get_db().table("system_health").insert({
            "component": component,
            "status": status,
            "message": message,
        }).execute()
    except Exception as e:
        log.warning("health log failed: %s", e)
