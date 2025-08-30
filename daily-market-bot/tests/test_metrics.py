import pandas as pd
from src.metrics import compute_sentiment_from_returns, compute_range_rating

def test_sentiment_rules():
    bullish = {"ret_1d": 0.01, "ret_5d": 0.02}
    bearish = {"ret_1d": -0.01, "ret_5d": -0.02}
    neutral = {"ret_1d": 0.0, "ret_5d": 0.0}

    assert compute_sentiment_from_returns(bullish) == "bullish"
    assert compute_sentiment_from_returns(bearish) == "bearish"
    assert compute_sentiment_from_returns(neutral) == "neutral"

def test_range_rating_low_buy():
    # fake series where last price = 10, low=10, high=20 (at the bottom)
    df = pd.DataFrame({"Adj Close": [10]*250 + [10]})
    result = compute_range_rating(df)
    assert result["rating"] in ["buy", "hold"]  # depending on momentum/trend
