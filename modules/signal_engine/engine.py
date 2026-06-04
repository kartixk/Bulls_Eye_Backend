"""Signal engine orchestration — pulls candles, computes indicators, persists signals."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from core.config import settings
from core.db import get_db
from modules.data_fetch.candle_store import CandleStore
from modules.signal_engine import indicators, rules
from modules.alerts.telegram_bot import send_signal_alert

log = logging.getLogger(__name__)

_IST = timezone(timedelta(hours=5, minutes=30))
_DEDUP_WINDOW = timedelta(minutes=15)
# key: "INSTRUMENT:ACTION", value: datetime of last signal
_last_signal: dict[str, datetime] = {}


def _is_duplicate(instrument: str, action: str) -> bool:
    key = f"{instrument}:{action}"
    last = _last_signal.get(key)
    if last is None:
        return False
    return (datetime.now(_IST) - last) < _DEDUP_WINDOW


def _record_signal(instrument: str, action: str) -> None:
    _last_signal[f"{instrument}:{action}"] = datetime.now(_IST)


def run_equity_signals(store: CandleStore) -> None:
    db = get_db()
    for sym in store.get_all_symbols():
        candles = store.get(sym, 60)
        if len(candles) < 21:
            continue
        df = indicators.to_df(candles)
        ind = indicators.compute(df)
        signal = rules.evaluate(sym, df["close"].iloc[-1], ind)
        if signal is None:
            continue
        if _is_duplicate(sym, signal["action"]):
            log.debug("dedup suppressed: %s %s", signal["action"], sym)
            continue
        signal["user_id"] = settings.OWNER_USER_ID
        try:
            inserted = db.table("signals").insert(signal).execute()
            _record_signal(sym, signal["action"])
            log.info("Signal stored: %s %s @ %s", signal["action"], sym, signal["entry_price"])
            if inserted.data:
                send_signal_alert(signal)
        except Exception as e:
            log.error("persist signal failed: %s", e)
