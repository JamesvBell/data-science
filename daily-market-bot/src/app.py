from datetime import date
from typing import List, Dict, Any
from html import escape

from fastapi import FastAPI, Query, Response

from metrics import fetch_prices, compute_metrics, compute_range_rating, compute_sentiment_from_returns
from llm import summarize_note
from io_local import load_headlines

DEFAULT_TICKERS = ["AAPL","MSFT","NVDA","AMZN","GOOGL","TSM","SAP","ASML","SONY"]

app = FastAPI(title="Daily Market Bot")

@app.get("/health")
def health():
    return {"status": "ok"}

def _compose_note_payload(ticker: str, as_of: str) -> Dict[str, Any]:
    df = fetch_prices(ticker)
    metrics = compute_metrics(df)
    range_info = compute_range_rating(df)
    det_sent = compute_sentiment_from_returns(metrics)

    try:
        headlines = load_headlines(as_of)
    except Exception:
        headlines = []

    note = summarize_note(
        as_of=as_of,
        ticker=ticker,
        metrics={**metrics, **range_info, "sentiment": det_sent},
        headlines=headlines,
    )

    return {
        "ticker": ticker,
        "as_of": as_of,
        "metrics": metrics,
        "rating": note.get("rating", range_info.get("rating", "hold")),
        "pos_pct_52w": range_info.get("pos_pct_52w", 0.5),
        "low_52w": range_info.get("low_52w"),
        "high_52w": range_info.get("high_52w"),
        "last": range_info.get("last"),
        "note": note.get("ticker_note", ""),
        "sentiment": note.get("sentiment", det_sent),
        "rationale": note.get("rationale", []),
        "risk_flags": note.get("risk_flags", []),
    }

@app.get("/daily-note/{ticker}")
def daily_note(ticker: str, as_of: str = Query(default=date.today().isoformat())):
    return _compose_note_payload(ticker, as_of)

@app.get("/daily-batch")
def daily_batch(
    tickers: List[str] = Query(default=DEFAULT_TICKERS),
    as_of: str = Query(default=date.today().isoformat())
):
    return {"as_of": as_of, "tickers": tickers, "data": [_compose_note_payload(t, as_of) for t in tickers]}

@app.get("/daily-report")
def daily_report(
    tickers: List[str] = Query(default=DEFAULT_TICKERS),
    as_of: str = Query(default=date.today().isoformat())
):
    rows = []
    for t in tickers:
        payload = _compose_note_payload(t, as_of)
        rows.append({
            "ticker": payload["ticker"],
            "last": float(payload.get("last", 0.0)),
            "ret_1d": float(payload["metrics"].get("ret_1d", 0.0)),
            "ret_5d": float(payload["metrics"].get("ret_5d", 0.0)),
            "vol_x": float(payload["metrics"].get("vol_vs_30d", 1.0)),
            "pos_pct_52w": float(payload.get("pos_pct_52w", 0.5)),
            "rating": str(payload.get("rating", "hold")).lower(),
            "sentiment": str(payload.get("sentiment", "neutral")).lower(),
            "note": str(payload.get("note", "")),
        })

    # small formatters
    def usd(x): return f"${x:,.2f}"
    def pct(x): return f"{x*100:+.2f}%"
    def mult(x): return f"{x:.2f}×"

    css = """
    <style>
      body { font-family: system-ui, Arial, sans-serif; margin: 24px; color:#111;}
      h1 { margin: 0 0 8px 0; }
      .meta { color:#666; margin-bottom:16px; }
      table { width: 100%; border-collapse: collapse; margin-top:12px; }
      th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
      th { background:#f7f7f7; text-align:left; }
      .pill { padding:2px 8px; border-radius:12px; font-size:12px; display:inline-block;}
      .buy { background:#e8f7ed; color:#137333; }
      .hold { background:#f5f5f5; color:#555; }
      .sell { background:#fdeaea; color:#a11; }
      .bullish { color:#137333; }
      .bearish { color:#a11; }
      .neutral { color:#555; }
      .note { color:#333; }
      .ticker { font-weight:600; letter-spacing:.2px; }
    </style>
    """

    header = f"<h1>Daily Market Report</h1><div class='meta'>As of {escape(as_of)} · {len(rows)} tickers</div>"

    table_head = """
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>1d Return</th>
            <th>5d Return</th>
            <th>Volume vs 30d</th>
            <th>52w Position</th>
            <th>Rating</th>
            <th>Sentiment</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>
    """

    table_rows = []
    for r in rows:
        rating = r["rating"]
        sent = r["sentiment"]
        table_rows.append(f"""
          <tr>
            <td class="ticker">{escape(r['ticker'])}</td>
            <td>{usd(r['last'])}</td>
            <td>{pct(r['ret_1d'])}</td>
            <td>{pct(r['ret_5d'])}</td>
            <td>{mult(r['vol_x'])}</td>
            <td>{r['pos_pct_52w']*100:.1f}%</td>
            <td><span class="pill {escape(rating)}">{escape(rating)}</span></td>
            <td class="{escape(sent)}">{escape(sent)}</td>
            <td class="note">{escape(r['note'])}</td>
          </tr>
        """)

    html = f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body>{header}{table_head}{''.join(table_rows)}</tbody></table></body></html>"
    return Response(content=html, media_type="text/html")
