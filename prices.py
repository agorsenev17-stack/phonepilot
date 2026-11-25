import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PRICES_FILE = BASE_DIR / "prices.json"

PHONES = [
    "iPhone 16",
    "Galaxy S25",
    "Xiaomi 15",
    "POCO X7 Pro",
    "OnePlus 13",
    "Pixel 9",
    "realme GT 7 Pro",
    "HONOR 200 Pro",
]


def calculate_average(prices):
    valid = [
        price for price in prices
        if isinstance(price, (int, float))
        and 1000 <= price <= 500000
    ]

    if not valid:
        return None

    valid.sort()

    if len(valid) >= 5:
        valid = valid[1:-1]

    return round(sum(valid) / len(valid))


def save_prices(data):
    result = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "phones": data,
    }

    PRICES_FILE.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def load_prices():
    if not PRICES_FILE.exists():
        return {}

    try:
        data = json.loads(
            PRICES_FILE.read_text(encoding="utf-8")
        )
        return data.get("phones", {})
    except (json.JSONDecodeError, OSError):
        return {}


def get_price(model):
    return load_prices().get(model, {}).get("average")


if __name__ == "__main__":
    print("PhonePilot: модуль цен готов.")
    print("Моделей в каталоге:", len(PHONES))
