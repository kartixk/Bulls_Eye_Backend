"""REST endpoints for the frontend."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from core.auth import require_internal_key
from core.config import settings
from core.db import get_db
from modules.data_fetch.candle_store import candle_store
from modules.data_fetch.fetch_cycle import INSTRUMENTS

api_bp = Blueprint("api", __name__, url_prefix="/api")

_IST = timezone(timedelta(hours=5, minutes=30))


@api_bp.get("/signals")
@require_internal_key
def list_signals():
    limit = int(request.args.get("limit", 100))
    db = get_db()
    res = (
        db.table("signals")
        .select("*")
        .eq("user_id", settings.OWNER_USER_ID)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return jsonify(res.data)


@api_bp.get("/health")
@require_internal_key
def health():
    db = get_db()
    res = db.table("system_health").select("*").order("recorded_at", desc=True).limit(20).execute()
    return jsonify(res.data)


@api_bp.post("/signals/<signal_id>/outcome")
@require_internal_key
def update_outcome(signal_id: str):
    body = request.get_json(silent=True) or {}
    outcome = body.get("outcome")
    if outcome not in {"WIN", "LOSS", "PARTIAL", "MISSED"}:
        return jsonify(error="invalid outcome"), 400
    db = get_db()
    db.table("signals").update({"outcome": outcome}).eq("id", signal_id).execute()
    return jsonify(ok=True)


@api_bp.get("/candles/<symbol>")
@require_internal_key
def get_candles(symbol: str):
    limit = int(request.args.get("limit", 300))
    candles = candle_store.get(symbol, limit)
    if not candles and symbol not in candle_store.get_all_symbols():
        return jsonify(error=f"Symbol {symbol!r} not found in store"), 404
    return jsonify(candles)


@api_bp.get("/status")
@require_internal_key
def get_status():
    # feed_live: use is_live() if available, else check if any symbol has data
    feed_live: bool = (
        candle_store.is_live()
        if callable(getattr(candle_store, "is_live", None))
        else bool(candle_store.get_all_symbols())
    )

    # last_update: use last_update attr if available
    raw_ltu = getattr(candle_store, "last_update", 0)
    ltu: float = raw_ltu if isinstance(raw_ltu, (int, float)) else 0
    last_update_str = datetime.fromtimestamp(ltu, _IST).isoformat() if ltu > 0 else None

    # signals_today: count from Supabase
    today_str = datetime.now(_IST).date().isoformat()
    db = get_db()
    try:
        res = (
            db.table("signals")
            .select("id", count="exact")
            .gte("created_at", today_str)
            .execute()
        )
        count = res.count or 0
    except Exception:
        count = 0

    return jsonify(feed_live=feed_live, last_update=last_update_str, signals_today=count)


@api_bp.get("/instruments")
@require_internal_key
def get_instruments():
    # WATCHED is list of (exchange, tradingsymbol, symboltoken) tuples
    names = [inst["name"] for inst in INSTRUMENTS]
    return jsonify(names)
