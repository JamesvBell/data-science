import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_headlines(date_str: str):
    path = DATA_DIR / "news" / f"{date_str}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
