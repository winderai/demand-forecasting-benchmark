# demand-forecasting-benchmark

Pretrained forecasters against the models a planner already has, on two kinds of public
demand data. Companion code for the Winder.AI article *Timestral Tested: AI Demand
Forecasting vs Your Spreadsheet*, published so that its numbers can be re-run rather than
believed. Every forecast the article reports is in `results/forecasts/`, and every number in
its tables comes out of `results/summary.json`.

- **Data:** weekly units for an online gift retailer (UCI Online Retail II, 2009-2011), and
  half-hourly GB national electricity demand (NESO), including the days after Timestral's
  release on 15 October 2026, which no model released before then can have seen. A small
  promotion test on FreshRetailNet-50K is the third.
- **Pretrained (zero-shot):** Timestral 5M and 209M (Mistral AI), Chronos-2 (Amazon),
  TimesFM 2.5 and TimesFM 3 (Google), t0-gamma and t0-beta (The Forecasting Company).
- **Fitted at every cut-off:** seasonal naive, AutoETS (a stand-in for Excel's
  `FORECAST.ETS`), Croston and TSB for intermittent demand, and LightGBM.
- **Measured:** MASE and weighted quantile loss (the GIFT-Eval conventions), each relative
  to seasonal naive; 10-90% band coverage; units short and left over if you order at the
  90th percentile; CPU time per series.
- **The key chart:** the same products forecast with 8, 13, 26, 52 and 78 weeks of history,
  to see whether a fitted model overtakes the pretrained ones once there is enough data.

<!-- RESULTS -->

## Running it

Python 3.12 and [uv](https://docs.astral.sh/uv/). About 6 GB of disk for the environment,
the data and the seven checkpoints. No GPU, no API keys, no Hugging Face token: every
checkpoint here is ungated.

```bash
uv sync --frozen                                   # pinned versions, Timestral from its git commit
uv run python scripts/download.py                  # public data -> data/raw, provenance -> data/manifest.json
uv run python scripts/prepare.py                   # -> data/prepared
uv run python scripts/run.py --family classical    # seasonal naive, AutoETS, Croston, TSB, LightGBM
uv run python scripts/run.py --family neural       # the pretrained models (the two can run at once)
uv run python scripts/score.py                     # -> results/summary.json, results/metrics_per_window.*
uv run python scripts/tables.py                    # -> results/tables.md (the tables below)
uv run python scripts/charts.py                    # -> charts/*.svg|png, results/demo.json
uv run python scripts/sanity.py                    # -> results/sanity.json
uv run pytest                                      # metric functions against hand-computed values
```

`run.py` caches each finished (task, model) pair under `results/forecasts/` and skips it next
time; `--force` reruns, `--only <model>` and `--part retail|grid|fresh` narrow it. The
classical and neural families run in separate processes because LightGBM's and PyTorch's
OpenMP runtimes crash each other in one process on macOS.

## Forecast one product with Timestral

`examples/one_product.py`, run on the prepared data:

```python
import pandas as pd
from timestral import TimestralForecaster

weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
sales = weekly[weekly["unique_id"] == "85123A"].set_index("ds")["y"]  # white hanging heart T-light holder
history = sales[:"2011-10-09"]

model = TimestralForecaster.from_pretrained("mistralai/Timestral-209M")
forecast = model.forecast(history.to_numpy(), prediction_length=8)

print(pd.DataFrame({
    "p10": forecast.quantile(0.1)[0, 0].numpy(), "median": forecast.median[0, 0].numpy(),
    "p90": forecast.quantile(0.9)[0, 0].numpy(), "actual": sales["2011-10-16":][:8].to_numpy(),
}, index=sales["2011-10-16":][:8].index).round(0))
```

<!-- EXAMPLE_OUTPUT -->

<!-- PROTOCOL -->
