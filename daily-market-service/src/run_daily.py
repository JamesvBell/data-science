from datetime import date
from metrics import fetch_prices, compute_metrics
from io_local import load_headlines

if __name__ == "__main__":
    as_of = date.today().isoformat()
    ticker = "AAPL"

    # 1. Load prices (CSV)
    df = fetch_prices(ticker)
    metrics = compute_metrics(df)

    # 2. Load headlines (JSON)
    headlines = load_headlines(as_of)  # expects data/news/YYYY-MM-DD.json

    # 3. Combine into dict
    note = {
        "ticker": ticker,
        "as_of": as_of,
        "metrics": metrics,
        "headlines": headlines,
    }

    print(note)
