# Daily Market Service
Daily Market Service is a FastAPI application that fetches live market data, computes transparent metrics in pandas, and uses an LLM for concise narrative summaries. It exposes health checks, JSON endpoints, and a daily HTML report for quick market insights.

This is a lightweight market “note generator” for learning and demos.  
It pulls prices with [yfinance](https://pypi.org/project/yfinance/), computes financial metrics with pandas, applies a transparent Buy/Hold/Sell framework, and (optionally) uses an LLM to add concise narrative summaries. Exposes JSON endpoints and a clean HTML report via FastAPI.

> ⚠️ Educational project only. Not investment advice.

---

## Business Problem

Finance and strategy teams often need **quick, explainable snapshots of market movements** — not just raw prices.  
Key questions stakeholders ask daily:

- How did key stocks move today?  
- Where are they relative to their 52-week range?  
- Should we view them as Buy, Hold, or Sell signals?  
- Can we share a one-paragraph narrative with leadership?  

This project addresses those needs with a system that keeps the **math deterministic in Python (pandas)** while letting the **LLM do what it’s good at: narrative and summarization**.

---

## Metrics

All metrics are computed in `metrics.py` using pandas. They are simple, transparent, and widely used in real finance settings.

1. **1-day return**  
   - Formula: `AdjClose[t] / AdjClose[t-1] - 1`  
   - Why: quick daily momentum snapshot, split/dividend adjusted.

2. **5-day return**  
   - Formula: `AdjClose[t] / AdjClose[t-5] - 1`  
   - Why: filters noise, shows short-term tone.

3. **Volume vs 30-day average**  
   - Formula: `Volume[t] / mean(Volume[t-29:t])`  
   - Why: >1.0 means heavier-than-normal trading activity (participation context).

4. **52-week range position**  
   - Formula: `(AdjClose[t] - min) / (max - min)` over trailing 252 trading days  
   - Why: shows where today’s price sits between its 52-week low and high. Legible to business users.

5. **Momentum confirmation**  
   - Formula: `AdjClose[t] / AdjClose[t-5] - 1`  
   - Why: prevents false “Buy” at lows if the price is still falling.

6. **Trend confirmation**  
   - Rule: 20-day SMA[t] > SMA[t-5] → uptrend  
   - Why: lightweight directional check, auditable.

---

## Deterministic Framework

- **Buy** if `pos_pct_52w ≤ 0.25` and (momentum ≥ 0 or trend up)  
- **Sell** if `pos_pct_52w ≥ 0.75` and (momentum ≤ 0 or trend down)  
- **Hold** otherwise  

**Sentiment rules**:  
- Bullish if 1-day return > +0.30% **and** 5-day return > +0.50%  
- Bearish if both are below those thresholds  
- Neutral otherwise  

All thresholds (`pct_low`, `pct_high`, `momentum_days`, `sma_window`, `slope_lookback`) are parameters in `metrics.py` — transparent and tunable.

---

## Why Python + LLM

- **Python (pandas)**: exact math, transparent thresholds, reproducible results.  
- **LLM (Claude)**: narrative skills — echo rating/sentiment, weave in rationale, produce ≤3-sentence “market note.”  
- **Result**: an **auditable + communicative** system, playing to each tool’s strengths.

---

## Repository Layout

daily-market-bot/
├─ src/
│ ├─ app.py # FastAPI app: endpoints + HTML rendering
│ ├─ metrics.py # Metrics, 52w range, Buy/Hold/Sell logic
│ ├─ llm.py # Claude API integration
│ ├─ io_local.py # Local headline loader (optional enrichment)
│ └─ run_daily.py # Runner script if scheduling
├─ data/ # optional local prices cache
├─ reports/ # optional saved HTML reports
├─ docs/
│ ├─ screenshots/
│ │ ├─ report_aapl_msft.png
│ │ └─ swagger_docs.png
│ ├─ sample_daily_note_AAPL.json
│ └─ todo.md
├─ tests/ # (future) unit tests for metrics
├─ requirements.txt
├─ README.md
└─ .gitignore


---

## What I Learned

- Designing **API endpoints** with FastAPI for health, single ticker, batch, and report.  
- Building **transparent, deterministic financial metrics** with pandas.  
- Splitting responsibilities: **math in code, narrative in LLM**.  
- Integrating with the **Claude API** for structured JSON summaries.  
- Producing a **clean HTML report** directly from Python (no JS frameworks).  
- Organizing a repo that’s **demo-ready for GitHub + LinkedIn**.  

---

## Quickstart

```bash
# create venv (Windows PowerShell example)
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# run the app
uvicorn app:app --reload --app-dir src

# open in browser
http://127.0.0.1:8000/daily-report

Endpoints

/health → simple status check

/daily-note/{ticker} → JSON with metrics, price, 52w features, rating, sentiment, note

/daily-batch?tickers=AAPL&tickers=MSFT → JSON for multiple tickers

/daily-report → HTML table for quick review

/docs → Swagger UI (interactive API docs)

Screenshots
<p align="center"> <img src="docs/screenshots/report_aapl_msft.png" width="760" alt="Daily Report Example"> </p> <p align="center"> <img src="docs/screenshots/swagger_docs.png" width="760" alt="Swagger UI Example"> </p>
Example JSON

See docs/sample_daily_note_AAPL.json
 for a sample /daily-note/AAPL response.

{
  "ticker": "AAPL",
  "as_of": "2025-08-29",
  "metrics": {
    "ret_1d": 0.0042,
    "ret_5d": 0.0125,
    "vol_vs_30d": 1.08
  },
  "rating": "hold",
  "pos_pct_52w": 0.62,
  "low_52w": 165.12,
  "high_52w": 233.90,
  "last": 221.45,
  "sentiment": "neutral",
  "note": "Brief, neutral one-to-three sentence summary appears here.",
  "rationale": ["Recent returns modest", "Position mid-range of 52w"],
  "risk_flags": []
}

Disclaimer

This project is for educational purposes only and does not constitute investment advice.
