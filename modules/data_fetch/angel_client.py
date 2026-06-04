"""Angel One SmartAPI client wrapper.

Authenticates with TOTP, exposes minimal methods for LTP + historical candles.
"""
from __future__ import annotations

import logging
from typing import Any

import pyotp
from SmartApi import SmartConnect

from core.config import settings

log = logging.getLogger(__name__)


class AngelOneClient:
    def __init__(self) -> None:
        self._sc: SmartConnect | None = None

    def _ensure(self) -> SmartConnect:
        if self._sc is not None:
            return self._sc
        sc = SmartConnect(api_key=settings.ANGEL_ONE_API_KEY)
        totp = pyotp.TOTP(settings.ANGEL_ONE_TOTP_SECRET).now()
        sc.generateSession(settings.ANGEL_ONE_CLIENT_ID, settings.ANGEL_ONE_PIN, totp)
        self._sc = sc
        log.info("Angel One session established")
        return sc

    def ltp(self, exchange: str, tradingsymbol: str, symboltoken: str) -> dict[str, Any]:
        return self._ensure().ltpData(exchange, tradingsymbol, symboltoken)

    def historical(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._ensure().getCandleData(params)


angel_client = AngelOneClient()
