# src/llm.py
import os
import json
from typing import List, Dict

def _fallback_note(as_of: str, ticker: str, metrics: Dict, headlines: List[Dict]) -> Dict:
    """Deterministic, no-API fallback."""
    titles = [f"{h.get('source','?')}: {h.get('title','')}" for h in headlines[:5]]
    dir_ = "up" if (metrics.get("ret_1d") or 0) >= 0 else "down"
    rating = metrics.get("rating", "hold")  # prefer deterministic rating computed upstream

    note = (
        f"{ticker} {dir_} {abs(metrics.get('ret_1d',0)):.2%} today. "
        f"Vol vs 30d avg: {metrics.get('vol_vs_30d',1.0):.2f}x. "
        f"Rating: {rating}. "
        f"Headlines: {'; '.join(titles) if titles else 'none available'}."
    )
    return {
        "ticker_note": note,
        "sentiment": "neutral",
        "rationale": titles,
        "risk_flags": ["llm_fallback_no_key"],
        "rating": rating,
    }

def summarize_note(as_of: str, ticker: str, metrics: Dict, headlines: List[Dict]) -> Dict:
    """
    Return JSON dict with keys:
      - ticker_note (str, <= 350 chars)
      - sentiment (one of: bullish, bearish, neutral)
      - rationale (List[str])
      - risk_flags (List[str])
      - rating (one of: buy, hold, sell)

    Prefers a precomputed 'rating' in `metrics` (echo it); only derive if missing.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_note(as_of, ticker, metrics, headlines)

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        # Claude instructions (short, strict, echo rating if provided)
        system = (
            "You are a concise, neutral market analyst. Write at most 3 sentences. No hype. "
            "Return ONLY compact JSON with keys: "
            "ticker_note (<= 350 chars), sentiment in {bullish, bearish, neutral}, "
            "rationale (list of short bullet strings), risk_flags (list), rating in {buy, hold, sell}. "
            "If a 'rating' is provided in the input metrics, ECHO that rating exactly. "
            "If rating is not provided, derive it using: "
            "below 52-week average -> buy; near average -> hold; above average -> sell. "
            "Do not include any extra fields or text."
        )

        # Keep payload minimal
        user = (
            f"As-of: {as_of}\nTicker: {ticker}\n"
            f"Metrics: {json.dumps(metrics, ensure_ascii=False)}\n"
            f"Headlines: {json.dumps(headlines[:5], ensure_ascii=False)}\n"
            "Respond with JSON only."
        )

        msg = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Extract plain text content
        text_parts = []
        for part in getattr(msg, "content", []):
            # parts can be objects with .text in anthropic SDK
            t = getattr(part, "text", None)
            if t:
                text_parts.append(t)
        text = "".join(text_parts).strip()

        data = json.loads(text)

        # Schema guard + echo deterministic rating if Claude omitted it
        for k in ["ticker_note", "sentiment", "rationale", "risk_flags", "rating"]:
            if k not in data:
                if k in ("rationale", "risk_flags"):
                    data[k] = []
                elif k == "rating":
                    data[k] = metrics.get("rating", "hold")
                else:
                    data[k] = ""

        # Final safety clamp on rating
        if data["rating"] not in {"buy", "hold", "sell"}:
            data["rating"] = metrics.get("rating", "hold")

        return data

    except Exception:
        # Any SDK/network/JSON error → robust deterministic fallback
        return _fallback_note(as_of, ticker, metrics, headlines)
