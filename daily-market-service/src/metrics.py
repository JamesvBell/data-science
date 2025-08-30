
import pandas as pd
from pathlib import Path
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "prices"

def load_prices(symbol: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / f"{symbol.upper()}.csv", parse_dates=["Date"])
    return df.sort_values("Date").reset_index(drop=True)

def compute_metrics(df: pd.DataFrame) -> dict:
    # Returns (as scalars)
    ret_1d = float(df["Adj Close"].pct_change(1).iloc[-1])
    ret_5d = float(df["Adj Close"].pct_change(5).iloc[-1])

    # Ensure Volume is a 1-D Series
    vol = df["Volume"]
    if isinstance(vol, pd.DataFrame):
        vol = vol.iloc[:, 0]

    # Robust 30-day average volume (works even if <30 rows by taking whatever is available)
    vol_30 = float(vol.tail(30).mean())
    curr_vol = float(vol.iloc[-1])
    vol_vs_30d = (curr_vol / vol_30) if vol_30 else 1.0

    return {"ret_1d": ret_1d, "ret_5d": ret_5d, "vol_vs_30d": vol_vs_30d}

def fetch_prices(symbol: str, period: str = "1y", interval: str = "1d"):
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, actions=False)
    return df.reset_index()

# ---------------- 52-week range features ----------------

def compute_52w_range_features(df: pd.DataFrame, window: int = 252) -> dict:
    """Returns 52w high/low and position of last price within that range."""
    adj = df["Adj Close"].tail(window)
    if isinstance(adj, pd.DataFrame):
        adj = adj.iloc[:, 0]

    last     = float(adj.iloc[-1])
    low_52w  = float(adj.min())
    high_52w = float(adj.max())
    rng = max(high_52w - low_52w, 1e-9)
    pos_pct = (last - low_52w) / rng  # 0 = at low, 1 = at high
    return {
        "last": last,
        "low_52w": low_52w,
        "high_52w": high_52w,
        "pos_pct_52w": pos_pct,
        "dist_to_low": (last - low_52w) / max(low_52w, 1e-9),
        "dist_to_high": (high_52w - last) / max(high_52w, 1e-9),
    }

def _simple_momentum(df: pd.DataFrame, days: int = 5) -> float:
    adj = df["Adj Close"]
    if isinstance(adj, pd.DataFrame):
        adj = adj.iloc[:, 0]
    if len(adj) <= days:
        return 0.0
    return float(adj.iloc[-1] / adj.iloc[-1 - days] - 1.0)

def _sma(series: pd.Series, n: int) -> pd.Series:
    # Ensure a 1-D Series even if a DataFrame slips through
    s = series
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s = pd.Series(s)
    return s.rolling(n, min_periods=n).mean()

def _trend_up(df: pd.DataFrame, sma_window: int = 20, slope_lookback: int = 5) -> bool:
    adj = df["Adj Close"]
    if isinstance(adj, pd.DataFrame):
        adj = adj.iloc[:, 0]

    # Need enough history for SMA and the lookback comparison
    if len(adj) < sma_window + slope_lookback:
        return False

    s = _sma(adj, sma_window).dropna()
    if len(s) < slope_lookback + 1:
        return False

    # Force scalar comparison to avoid pandas truth-value ambiguity
    last = float(s.iloc[-1])
    prev = float(s.iloc[-1 - slope_lookback])
    return last > prev

def compute_range_rating(
    df: pd.DataFrame,
    pct_low: float = 0.25,
    pct_high: float = 0.75,
    momentum_days: int = 5,
    sma_window: int = 20,
    slope_lookback: int = 5,
) -> dict:
    """
    Buy/Hold/Sell using 52w range position with momentum/trend confirmation.
    - If pos in lower quartile and (momentum >= 0 or trend up) -> buy
    - If pos in upper quartile and (momentum <= 0 or trend down) -> sell
    - Else -> hold
    """
    feats = compute_52w_range_features(df)
    pos = float(feats["pos_pct_52w"])
    mom = _simple_momentum(df, momentum_days)
    up = _trend_up(df, sma_window, slope_lookback)

    if pos <= pct_low and (mom >= 0 or up):
        rating = "buy"
    elif pos >= pct_high and (mom <= 0 or not up):
        rating = "sell"
    else:
        rating = "hold"

    return {
        "rating": rating,
        **feats,  # includes last, low_52w, high_52w, pos_pct_52w, dist_to_*
        "momentum_%": mom,
        "trend_up": up,
        "params": {
            "pct_low": pct_low,
            "pct_high": pct_high,
            "momentum_days": momentum_days,
            "sma_window": sma_window,
            "slope_lookback": slope_lookback,
        },
    }

# ---------------- Deterministic sentiment ----------------

def compute_sentiment_from_returns(metrics: dict,
                                   eps_1d: float = 0.003,   # 0.30%
                                   eps_5d: float = 0.005):  # 0.50%
    r1 = float(metrics.get("ret_1d", 0.0))
    r5 = float(metrics.get("ret_5d", 0.0))
    if r1 > eps_1d and r5 > eps_5d:
        return "bullish"
    if r1 < -eps_1d and r5 < -eps_5d:
        return "bearish"
    return "neutral"
