"""Rule-based signal generation for equities.

Bullish: RSI < 30 (oversold) + close > EMA21 + volume_ratio > 1.5.
Bearish: RSI > 70 (overbought) + close < EMA21 + volume_ratio > 1.5.
"""
from __future__ import annotations

from typing import Optional

from core.types import Signal


def evaluate(symbol: str, close: float, ind: dict[str, float]) -> Optional[Signal]:
    if not ind:
        return None
    rsi, ema21, vol = ind["rsi"], ind["ema21"], ind["volume_ratio"]
    action: str | None = None
    rationale: str = ""

    if rsi < 30 and close > ema21 and vol > 1.5:
        action = "BUY"
        rationale = f"Oversold reversal: RSI {rsi:.1f}, close>{ema21:.2f}, vol×{vol:.1f}"
    elif rsi > 70 and close < ema21 and vol > 1.5:
        action = "SELL"
        rationale = f"Overbought breakdown: RSI {rsi:.1f}, close<{ema21:.2f}, vol×{vol:.1f}"

    if action is None:
        return None

    confidence = min(100.0, 50 + abs(50 - rsi) + (vol - 1) * 10)
    tp = close * (1.02 if action == "BUY" else 0.98)
    sl = close * (0.99 if action == "BUY" else 1.01)

    return {
        "instrument": symbol,
        "kind": "EQUITY",
        "action": action,  # type: ignore[typeddict-item]
        "entry_price": float(close),
        "target_price": round(tp, 2),
        "stop_loss": round(sl, 2),
        "confidence": round(confidence, 2),
        "rsi": round(rsi, 2),
        "macd": round(ind.get("macd", 0.0), 4),
        "ema21": round(ema21, 2),
        "volume_ratio": round(vol, 2),
        "rationale": rationale,
    }
