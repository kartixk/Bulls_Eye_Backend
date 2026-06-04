"""Unit tests for the rule engine."""
from __future__ import annotations

from modules.signal_engine import rules


def test_no_signal_when_indicators_empty():
    assert rules.evaluate("X", 100.0, {}) is None


def test_buy_on_oversold_with_volume():
    ind = {"rsi": 25.0, "macd": 0.1, "ema21": 99.0, "volume_ratio": 2.0}
    sig = rules.evaluate("RELIANCE", 100.0, ind)
    assert sig is not None
    assert sig["action"] == "BUY"
    assert sig["target_price"] > sig["entry_price"]
    assert sig["stop_loss"] < sig["entry_price"]


def test_sell_on_overbought_with_volume():
    ind = {"rsi": 78.0, "macd": -0.1, "ema21": 101.0, "volume_ratio": 2.5}
    sig = rules.evaluate("TCS", 100.0, ind)
    assert sig is not None
    assert sig["action"] == "SELL"
