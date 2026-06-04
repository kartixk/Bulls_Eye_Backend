"""Technical indicators — native pandas/numpy, no pandas-ta dependency."""
from __future__ import annotations

import numpy as np
import pandas as pd

from core.types import Candle


def to_df(candles: list[Candle]) -> pd.DataFrame:
    df = pd.DataFrame(candles)
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df.set_index("timestamp")


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=length - 1, min_periods=length).mean()
    avg_loss = loss.ewm(com=length - 1, min_periods=length).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    """Return MACD line (fast EMA - slow EMA)."""
    return _ema(series, fast) - _ema(series, slow)


def compute(df: pd.DataFrame) -> dict[str, float]:
    """Return latest RSI, MACD, EMA21, volume ratio."""
    if len(df) < 21:
        return {}
    close = df["close"]
    rsi_val = _rsi(close).iloc[-1]
    macd_val = _macd(close).iloc[-1]
    ema21_val = _ema(close, 21).iloc[-1]
    avg_vol = df["volume"].rolling(20).mean().iloc[-1]
    vol_ratio = df["volume"].iloc[-1] / avg_vol if avg_vol and avg_vol > 0 else 1.0
    return {
        "rsi": float(rsi_val) if not np.isnan(rsi_val) else 50.0,
        "macd": float(macd_val) if not np.isnan(macd_val) else 0.0,
        "ema21": float(ema21_val),
        "volume_ratio": float(vol_ratio),
    }
