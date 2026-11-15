# btc-cent-forecast-01, variant w3: mean-reversion to the 24h median.
#
# Forecast for 240 minutes after the checkpoint:
#   forecast = last_close
#            + 0.15 * (median of the last 1440 closes - last_close)
#            + 0.05 * (last_close - close 60 minutes ago)
# The total shift is clamped to +/-1.5% of last_close.
# Fallback: if fewer than 100 prices are present, forecast = last_close.
#
# Python 3.13, standard library only, no network, deterministic.

import json
import math
import os
import statistics
from pathlib import Path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

MEAN_REVERSION_WEIGHT = 0.15
MOMENTUM_WEIGHT = 0.05
MEDIAN_WINDOW = 1440          # last 24 hours of 1-minute closes
MOMENTUM_LAG = 60             # last 60 minutes
MAX_SHIFT_FRACTION = 0.015    # clamp the shift to +/-1.5% of last_close
MIN_PRICES = 100


def price5(x):
    """Keep x on the grid's 5 decimals and inside (0, 10_000_000)."""
    x = min(MAX_PRICE, max(MIN_PRICE, x))
    return round(x, 5)


def forecast(prices):
    """Mean-reversion-to-24h-median forecast for one market's closes."""
    if not prices:
        raise ValueError("market has no prices")
    last = prices[-1]
    if not isinstance(last, (int, float)) or not math.isfinite(last):
        raise ValueError("market's last price is not a finite number")

    if len(prices) < MIN_PRICES:
        return price5(last)

    window = prices[-MEDIAN_WINDOW:]
    # Any non-finite value in the window (should not happen on the grid)
    # falls back to persistence rather than poisoning the forecast.
    if not all(isinstance(p, (int, float)) and math.isfinite(p) for p in window):
        return price5(last)
    median24h = statistics.median(window)

    change60 = last - prices[-1 - MOMENTUM_LAG]
    shift = MEAN_REVERSION_WEIGHT * (median24h - last) + MOMENTUM_WEIGHT * change60

    max_shift = MAX_SHIFT_FRACTION * last
    shift = max(-max_shift, min(max_shift, shift))
    return price5(last + shift)


def main():
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = sorted(p.name for p in input_dir.iterdir() if p.name.endswith(".in"))
    for name in inputs:
        case_id = name[:-3]
        with open(input_dir / name, "r", encoding="utf-8") as f:
            case = json.load(f)
        markets = case.get("markets")
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{name} does not hold exactly one market")
        price = forecast(markets[0]["prices"])
        payload = {"forecasts": [{"case": case_id, "price": price}]}
        with open(output_dir / f"{case_id}.out", "w", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")


if __name__ == "__main__":
    main()
