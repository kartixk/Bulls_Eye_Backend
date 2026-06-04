"""Telegram alert dispatcher."""
from __future__ import annotations

import logging
import requests

from core.config import settings
from core.types import Signal
from .formatter import format_signal

log = logging.getLogger(__name__)

API = "https://api.telegram.org/bot{token}/sendMessage"


def _send(text: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured; skipping")
        return
    try:
        r = requests.post(
            API.format(token=settings.TELEGRAM_BOT_TOKEN),
            json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        if r.status_code != 200:
            log.warning("telegram %s %s", r.status_code, r.text)
    except Exception as e:  # pragma: no cover
        log.error("telegram send failed: %s", e)


def send_signal_alert(signal: Signal) -> None:
    _send(format_signal(signal))


def send_morning_briefing(text: str) -> None:
    _send(f"☀️ *Morning briefing*\n{text}")


def send_eod_summary(text: str) -> None:
    _send(f"🌙 *EOD summary*\n{text}")
