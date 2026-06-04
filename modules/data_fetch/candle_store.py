"""In-memory rolling candle store, keyed by symbol."""
from __future__ import annotations
import time
from collections import deque
from typing import Deque
from core.types import Candle


class CandleStore:
    def __init__(self, maxlen: int = 300) -> None:
        self._store: dict[str, Deque[Candle]] = {}
        self._maxlen = maxlen
        self.last_update: float = 0.0

    def update(self, symbol: str, candle: Candle) -> None:
        dq = self._store.setdefault(symbol, deque(maxlen=self._maxlen))
        dq.append(candle)
        self.last_update = time.time()

    def get(self, symbol: str, n: int = 60) -> list[Candle]:
        dq = self._store.get(symbol)
        return list(dq)[-n:] if dq else []

    def get_all_symbols(self) -> list[str]:
        return list(self._store.keys())

    def is_live(self, max_stale_seconds: int = 180) -> bool:
        return self.last_update > 0 and (time.time() - self.last_update) < max_stale_seconds


candle_store = CandleStore()
