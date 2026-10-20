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

## What was run, exactly

### Data

| Dataset | Source | Licence (as stated on the source page) | Downloaded |
|---|---|---|---|
| Online Retail II | [UCI ML Repository, id 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii) | CC BY 4.0 | 20 Oct 2026 |
| Historic Demand Data 2024-2026 | [NESO data portal](https://www.neso.energy/data-portal/historic-demand-data) | [NESO Open Data Licence](https://www.neso.energy/data-portal/ngeso-open-licence) | 20 Oct 2026 |
| Demand Data Update (latest actuals) | [NESO data portal](https://www.neso.energy/data-portal/daily-demand-update) | NESO Open Data Licence | 20 Oct 2026 |
| TEMP, GB daily average temperature | [Elexon BMRS](https://bmrs.elexon.co.uk/temperature) | [BMRS Data Licence](https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/) | 20 Oct 2026 |
| FreshRetailNet-50K | [Hugging Face, Dingdong-Inc](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K) | CC BY 4.0 | 20 Oct 2026 |

Contains BMRS data © Elexon Limited copyright and database right 2026. Contains data from the
National Energy System Operator (NESO). URLs, byte counts and SHA-256 hashes of every file are
in `data/manifest.json`; cleaning counts are in `data/prepared/*_notes.json`.

**Retail.** Cancellations (invoices starting `C`), the original lines they cancel (6,485
lines, 407,924 units, matched on customer, StockCode and quantity to the latest earlier
order; without this a cancelled order of 74,215 storage jars on 18 Jan 2011 stays in the
data as a real sale), lines with a quantity or price of zero or less, and every StockCode that is not a product (postage, carriage, manual adjustments, bank
charges, Amazon fees, samples, gift vouchers, test codes, the `DCGS` web-shop codes) are
dropped; a product code is five digits plus an optional letter. Units are summed per StockCode
over all countries into weeks ending Sunday. The partial first week (data starts on a Tuesday)
and the partial last week (data ends on a Friday) are dropped, leaving 104 full weeks, 13 Dec
2009 to 4 Dec 2011. Each product's series starts at its first week with a sale and is
zero-filled after it.

**Grid.** The target is ND, national demand: what transmission-connected generation must
meet, excluding station load, pumped-storage pumping and interconnector exports. TSD adds
those back, and pumping and exports follow prices rather than weather and behaviour, so ND is
the demand a forecaster is asked about. Settlement periods are mapped to UTC half-hours (clock
changes give 46 or 50 periods). NESO's yearly Historic Demand Data file for 2026 ends on 29
September, so the days since come from NESO's Demand Data Update, which carries the same
columns and agrees exactly with the yearly file where they overlap (1-29 Sep 2026). NESO
flags data issues on that update for 3-13 October 2026, under review when downloaded; those
days sit in the context of the leak-free forecasts and are used as published. Two half-hours
are missing (15 Oct 23:30 and 16 Oct 00:00 UK time) and are left out of scoring.

**Temperature** is BMRS TEMP, the daily GB average temperature, repeated across the 48
half-hours of its day. It is a measured outturn, not a forecast, so every "+ temperature" row
is an **oracle covariate**: the model is told the day's actual average temperature in advance.
A real day-ahead forecast would do somewhat worse. Open-Meteo's archived forecasts were
considered and not used because its free API is for non-commercial use only.

**FreshRetailNet-50K** has 90 days of training and a 7-day evaluation week (26 Jun - 2 Jul
2024) for each of 50,000 store-product series of a Chinese fresh-food retailer, with a daily
discount rate, a holiday flag and an activity flag. The test samples 400 series (seed 2026)
from the {{FRESH_CANDIDATES}} whose discount changes during the evaluation week, so a model that is told the
planned discount has something to use. Sales there are rescaled by the publisher and are
censored on stock-out days. No promotion dataset from Kaggle (M5, Favorita, Rossmann) is used:
their terms do not allow redistribution.

### Backtest

| | Retail | Grid, historic | Grid, leak-free | FreshRetailNet |
|---|---|---|---|---|
| Horizon | 8 weeks | 48 half-hours (one day) | 48 half-hours | 7 days |
| Cut-offs | weeks ending 19 Jun, 17 Jul, 14 Aug, 11 Sep, 9 Oct 2011 | UK midnight on 28 days of 2025: 13-19 Jan, 28 Apr-4 May, 7-13 Jul, 6-12 Oct | UK midnight on 15, 16, 17, 18 and 19 Oct 2026 | 25 Jun 2024 |
| Series | 300 products sampled at random (seed 2026) from the 3,295 eligible | 1 | 1 | 400 |
| Windows | 1,332 | 28 | 5 | 400 |
| Context for pretrained models | each product's full history (8 to 95 weeks) | last 4,096 half-hours (85 days) | last 4,096 half-hours | all 90 days |
| Fitted models train on | each window's own history (AutoETS, Croston, TSB); all sampled products' histories at that cut-off (LightGBM) | AutoETS: the same 4,096 half-hours; LightGBM: the 365 days before the cut-off | as historic | AutoETS: each series; LightGBM: all 400 |

A (product, cut-off) pair is eligible when the product has at least 8 weeks of history, sold
something in the 13 weeks before the cut-off (it is still on sale), and its history is not
constant. The leak-free window holds every day-ahead forecast whose targets start at or after
00:00 UK time on 15 October 2026 (23:00 UTC on 14 October) and for which NESO had published
the whole day by 20 October; Timestral and its weights were released that day, t0-gamma on 12
October, and every other checkpoint earlier.

**History-length sweep.** Retail: 80 of the sampled products with at least 78 weeks of history
at a cut-off (342 windows), each forecast five times with its context cut to its last 8, 13,
26, 52 and 78 weeks. The targets and the MASE scale (from the full history) stay the same, so
only the history changes. LightGBM is refitted on the truncated histories. Grid: 12 of the
historic cut-offs (the Monday, Thursday and Saturday of each block), with 48, 336, 1,344 and
4,032 half-hours (a day, a week, four weeks, twelve weeks) and no temperature for any model;
LightGBM is fitted on the truncated context alone.

### Contenders

| Model | What it is here |
|---|---|
| Seasonal naive | Retail: the same week last year when the history covers 52 weeks, else the last week's value. Grid: the same half-hour a week earlier. FreshRetailNet: the same day a week earlier. |
| AutoETS | `statsforecast` 2.1.1 `AutoETS`, season 52 (retail), 48 (grid), 7 (FreshRetailNet); automatic model selection; intervals from the model at 20/40/60/80% give the nine quantiles. A stand-in for Excel's `FORECAST.ETS`, which fits an additive (AAA) ETS model: not the same code. {{ETS_SEASONAL_NOTE}} |
| Croston, TSB | `CrostonOptimized` and `TSB(alpha_d=0.1, alpha_p=0.1)`, retail only. Point forecasts: their nine "quantiles" are the point, so their WQL is a point forecast's, and coverage and the p90 order are not reported. |
| LightGBM | `mlforecast` 1.1.0 with `lightgbm` 4.7.0, quantile objective, one model per quantile, 200 trees, learning rate 0.05, 31 leaves, one thread. Retail: global over all sampled products at each cut-off, lags 1-4, 8, 13, 26, 52, rolling means of 4 and 13 weeks, expanding mean, week of year and month, direct multi-horizon (one model per quantile per step). Grid: lags of 1, 2, 3, 7 and 14 days, rolling means of a day and a week, half-hour of day, day of week, day of year, plus temperature in the "+ temperature" rows; every lag is at least a day, so the day-ahead forecast never feeds on itself. Quantiles sorted. |
| Timestral 5M, 209M | `timestral` at git commit `a534bdbd244d64f3d9d743f46c7bf6fc330ed4ff` (no PyPI release or tag exists), `forecast()` defaults: symmetric averaging on (two passes), non-negative clipping on. Temperature and calendar rows as `known_covariates`. |
| Chronos-2 | `chronos-forecasting` 2.3.2, `Chronos2Pipeline.predict_quantiles`, defaults, no cross-learning; temperature as a past and future covariate. |
| TimesFM 2.5 | `timesfm` 3.0.2, `TimesFM_2p5_200M_torch` with its model card's flags. No covariates: TimesFM 2.5 takes them only through XReg, which needs JAX. |
| TimesFM 3 | `timesfm` 3.0.2, `TimesFM3Evaluator` (its benchmark defaults: symmetric averaging, non-negativity); temperature as a past-and-future covariate. **Its weights are under Google's TimesFM Non-Commercial Licence**: fine for this research benchmark, not deployable in a commercial product. |
| t0-gamma, t0-beta | `tfc-t0` 0.6.0, `T0Forecaster.predict` with the four adjustments its model card recommends switched on (trim leading missing, symmetric averaging, clip non-negative, snap integers); temperature as a future covariate. |

Every pretrained model runs zero-shot, with no fine-tuning, on the CPU. Every model's point
forecast is its median. Every retail and FreshRetailNet quantile is clipped at zero, for every
contender.

### Metrics

- **MASE**: mean absolute error of the median over the mean absolute seasonal difference of the
  in-sample history, with the GIFT-Eval (GluonTS) seasonality: 1 for weekly and daily data, 48
  for half-hourly. Retail and FreshRetailNet are scaled by period-1 differences.
- **WQL**: for each quantile level 0.1, 0.2, ... 0.9, twice the summed pinball loss over the
  summed absolute target, then the mean over levels: GIFT-Eval's CRPS proxy. "WQL" in the tables
  is pooled over all windows of a task, as GIFT-Eval pools over a dataset.
- **Relative MASE** is the geometric mean, over windows, of each model's MASE over seasonal
  naive's on the same window, skipping windows where either is zero (all-zero targets forecast
  as zero); the 95% interval resamples whole series. **Relative WQL** is pooled WQL over
  seasonal naive's pooled WQL. Both: lower is better, below 1 beats seasonal naive.
- **Coverage**: the share of actuals inside the 10-90% band; a calibrated model gets 0.80.
- **Ordering at the 90th percentile** (retail): each week's order is the model's
  90th-percentile forecast; units short are demand above the order, units over are the order
  above demand, summed over every window. This is a convention, not an optimum: ordering at
  the 90th percentile is right only when a unit short costs nine times a unit left over.
- **Time**: wall-clock forecast time per window on the CPU, excluding loading, which is
  reported separately. Fitted models' times include fitting.

