"""Typed dicts used across modules — mirrors frontend ISignal."""
from __future__ import annotations
from typing import Literal, TypedDict, Optional

SignalAction = Literal["BUY", "SELL"]
SignalKind = Literal["EQUITY", "FNO"]


class Candle(TypedDict):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class Signal(TypedDict, total=False):
    user_id: str
    instrument: str
    kind: SignalKind
    action: SignalAction
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    confidence: float
    rsi: Optional[float]
    macd: Optional[float]
    ema21: Optional[float]
    volume_ratio: Optional[float]
    strike_price: Optional[float]
    expiry_date: Optional[str]
    premium: Optional[float]
    rationale: Optional[str]
