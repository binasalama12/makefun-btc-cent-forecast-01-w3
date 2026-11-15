# btc-cent-forecast-01 — variant w3: mean-reversion to the 24h median

Forecast Bitcoin's price 240 minutes after each checkpoint.

## Approach

Bitcoin's 1-minute closes tend to drift back toward their recent centre over a
few hours, while short-term moves carry a little momentum. This entry combines
both, with a hard cap on how far the guess may move from the checkpoint close:

```
forecast = last_close
         + 0.15 × (median of the last 1440 closes − last_close)
         + 0.05 × (last_close − close 60 minutes ago)
```

- **Median of the last 1440 closes (24h):** a robust centre that ignores the
  pool's occasional one-minute spikes better than a mean does.
- **60-minute change:** a small momentum term; a price that has been rising
  over the last hour is nudged a little further up, and vice versa.
- **Clamp:** the total shift is limited to ±1.5% of `last_close`, so a wild
  median gap or a sharp 60-minute move can never drag the guess far away.
- **Fallback:** with fewer than 100 prices the forecast is just `last_close`
  (persistence), and any non-finite value in the window falls back the same way.

## Files

- `main.py` — entrypoint. Python 3.13, standard library only, no network,
  deterministic (same input → same output bytes). Reads every `*.in` in
  `$MAKEFUN_INPUT_DIR` (else `/input`), writes `<id>.out` to
  `$MAKEFUN_OUTPUT_DIR` (else `/output`) as
  `{"forecasts":[{"case":"<id>","price":<number>}]}`.
- `LICENSE` — MIT (copied from the kit's starter).

## Run locally

```sh
mkdir -p /tmp/btc-w3-out
MAKEFUN_INPUT_DIR=~/workspace/makefun/kits/btc-cent-forecast-01-kit/input \
MAKEFUN_OUTPUT_DIR=/tmp/btc-w3-out python3 main.py
```
