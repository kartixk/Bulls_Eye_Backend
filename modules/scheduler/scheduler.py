"""APScheduler setup — IST market-hour jobs."""
from __future__ import annotations

import logging

# pyrefly: ignore [missing-import]
from apscheduler.schedulers.background import BackgroundScheduler
# pyrefly: ignore [missing-import]
from apscheduler.triggers.cron import CronTrigger
from flask_socketio import SocketIO

from core.config import settings
from modules.data_fetch.fetch_cycle import fetch_cycle, warm_up
from modules.signal_engine.fno_strategy import run_fno_cycle
from modules.alerts.telegram_bot import send_morning_briefing, send_eod_summary

log = logging.getLogger(__name__)
_started = False


def start_scheduler(sio: SocketIO) -> None:  # noqa: ARG001 — sio kept for API compat
    global _started
    if _started:
        return
    sched = BackgroundScheduler(timezone=settings.TZ)

    # Warm-up job at 09:00 IST on weekdays — pre-loads candle history
    sched.add_job(
        warm_up,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=0),
        id="warm_up",
        max_instances=1,
        coalesce=True,
    )

    # 1-min equity fetch, weekdays 09:00–15:59 IST (is_market_hours() guards 9:15 start)
    sched.add_job(
        fetch_cycle,
        CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*/1"),
        id="fetch_cycle",
        max_instances=1,
        coalesce=True,
    )

    # 5-min F&O option chain
    sched.add_job(
        run_fno_cycle,
        CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*/5"),
        id="fno_cycle",
        max_instances=1,
        coalesce=True,
    )

    # Morning briefing at 09:15 IST
    sched.add_job(
        lambda: send_morning_briefing("Markets open. Engine armed."),
        CronTrigger(day_of_week="mon-fri", hour=9, minute=15),
        id="morning",
    )

    # EOD summary at 15:35 IST
    sched.add_job(
        lambda: send_eod_summary("Markets closed. Engine sleeping."),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=35),
        id="eod",
    )

    sched.start()
    _started = True
    log.info("Scheduler started (tz=%s)", settings.TZ)
