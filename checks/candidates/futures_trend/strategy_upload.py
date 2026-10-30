# User upload 2026-10-30 (QuantJourney Backtester example 25, Apache 2.0): the signal and weight function, as given.
import numpy as np
import pandas as pd


def build_continuous_futures_trend(close: pd.DataFrame, *, fast_window: int = 63, slow_window: int = 252,
                                   volatility_window: int = 63) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return moving-average trend signals and unit-gross inverse-vol weights."""
    fast = close.rolling(fast_window, min_periods=fast_window).mean()
    slow = close.rolling(slow_window, min_periods=slow_window).mean()
    valid = fast.notna() & slow.notna()
    signals = np.sign(fast - slow).where(valid, 0.0).astype(float)
    volatility = close.pct_change(fill_method=None).rolling(volatility_window, min_periods=volatility_window).std() * np.sqrt(252.0)
    raw = signals / volatility.replace(0.0, np.nan)
    weights = raw.div(raw.abs().sum(axis=1).replace(0.0, np.nan), axis=0).fillna(0.0)
    return signals, weights
# Original run: instruments MES=F, MNQ=F, ZN=F, CL=F, GC=F, ZC=F; 2019-05-06 .. 2026-01-01; $1,000,000; monthly ('BME') rebalance.
