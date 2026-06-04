"""1-minute fetch cycle for equities — runs during market hours."""
from __future__ import annotations
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from modules.data_fetch.angel_client import angel_client
from modules.data_fetch.candle_store import candle_store
from modules.signal_engine.engine import run_equity_signals
from core.types import Candle
from core.sio import get_sio
from core.health import log_health_event

log = logging.getLogger(__name__)

# IST = UTC+5:30
_IST = timezone(timedelta(hours=5, minutes=30))

# Load instrument list from data/nifty100.json
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "nifty100.json"
INSTRUMENTS: list[dict[str, str]] = json.loads(_DATA_FILE.read_text())


def _now_ist() -> datetime:
    return datetime.now(_IST)


def is_market_hours() -> bool:
    now = _now_ist()
    if now.weekday() >= 5:   # Saturday / Sunday
        return False
    open_t = now.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_t <= now <= close_t


def warm_up() -> None:
    """Fetch last 65 min of 1-min candles for every instrument at market open."""
    log.info("warm_up: fetching historical candles for %d instruments", len(INSTRUMENTS))
    now = _now_ist()
    from_dt = (now - timedelta(minutes=65)).strftime("%Y-%m-%d %H:%M")
    to_dt = now.strftime("%Y-%m-%d %H:%M")

    loaded = 0
    for inst in INSTRUMENTS:
        try:
            resp = angel_client.historical({
                "exchange": inst["exchange"],
                "symboltoken": inst["symboltoken"],
                "interval": "ONE_MINUTE",
                "fromdate": from_dt,
                "todate": to_dt,
            })
            rows = resp.get("data") or []
            for row in rows:
                # row: [timestamp_str, open, high, low, close, volume]
                ts_str, o, h, l, c, v = row
                # parse ISO timestamp like "2024-01-01T09:15:00+05:30"
                try:
                    dt = datetime.fromisoformat(ts_str)
                    ts = int(dt.timestamp())
                except Exception:
                    ts = int(time.time())
                candle: Candle = {
                    "timestamp": ts,
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": float(v),
                }
                candle_store.update(inst["name"], candle)
            loaded += 1
        except Exception as e:
            log.warning("warm_up %s failed: %s", inst["name"], e)
        time.sleep(0.4)   # stay within Angel One rate limits

    log.info("warm_up complete: %d/%d instruments loaded", loaded, len(INSTRUMENTS))
    log_health_event("data_feed", "WARM_UP_DONE", f"{loaded}/{len(INSTRUMENTS)} instruments")


def fetch_cycle() -> None:
    """Pull LTP for each instrument, append synthetic candle, run signals, emit WebSocket event."""
    if not is_market_hours():
        return

    start = time.time()
    sio = get_sio()
    successes = 0

    for inst in INSTRUMENTS:
        try:
            data = angel_client.ltp(inst["exchange"], inst["tradingsymbol"], inst["symboltoken"])
            ltp = data.get("data", {}).get("ltp")
            if ltp is None:
                continue
            now_ts = int(time.time())
            candle: Candle = {
                "timestamp": now_ts,
                "open": float(ltp),
                "high": float(ltp),
                "low": float(ltp),
                "close": float(ltp),
                "volume": 0.0,
            }
            candle_store.update(inst["name"], candle)
            if sio:
                sio.emit(
                    "candle:update",
                    {"symbol": inst["name"], "candle": candle},
                    to=f"sym:{inst['name']}",
                )
            successes += 1
        except Exception as e:
            log.warning("fetch %s failed: %s", inst["name"], e)

    run_equity_signals(candle_store)

    elapsed = time.time() - start
    if successes > 0:
        log_health_event("data_feed", "FEED_LIVE", f"{successes} instruments in {elapsed:.1f}s")
    else:
        log_health_event("data_feed", "FEED_STALE", "0 successful LTP fetches")
        log.error("fetch_cycle: all %d instruments failed", len(INSTRUMENTS))

    log.info("fetch_cycle done: %d/%d ok in %.2fs", successes, len(INSTRUMENTS), elapsed)
