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
  `FORECAST.ETS`; on the grid also ETS(A,A,A), Excel's model structure), Croston and TSB for
  intermittent demand, and LightGBM.
- **Measured:** MASE and weighted quantile loss (the GIFT-Eval conventions), each relative
  to seasonal naive; 10-90% band coverage; units short and left over if you order at the
  90th percentile; CPU time per series.
- **The key chart:** the same products forecast with 8, 13, 26, 52 and 78 weeks of history,
  to see whether a fitted model overtakes the pretrained ones once there is enough data.

## Results

Run on 20 October 2026 on an Apple M1 (8 cores, 16 GB), CPU only, PyTorch at 8 threads.
Lower is better everywhere except coverage, which should be near 0.80. "Rel." columns are
ratios to seasonal naive on the same windows (below 1 beats it). Every figure is in
`results/summary.json`; per-window metrics are in `results/metrics_per_window.parquet`.

![Relative MASE and WQL by model](charts/results_bars.svg)

**What the numbers say, in plain terms:**

- **Retail.** Every pretrained model beat every fitted model except LightGBM, which sits
  inside the pretrained pack: on relative MASE it is ahead of t0-gamma and t0-beta and behind
  Timestral, Chronos-2 and the two TimesFMs; on WQL it is behind all seven. The 95% intervals
  of the top five pretrained models overlap each other, and Timestral 209M's (0.42-0.52)
  overlaps LightGBM's (0.49-0.59). AutoETS, Croston and TSB beat seasonal naive but trail
  every pretrained model.
- **History length (the sweep).** On these 80 products no fitted model overtakes the best
  pretrained model at any history length from 8 to 78 weeks, on relative MASE, relative WQL
  or mean MASE. LightGBM gets closest at 52 weeks (relative MASE 0.533 against 0.443 for
  Timestral 5M; mean MASE 1.127 against 1.067 for Timestral 209M). There is no crossover in
  this data. On GB demand the sweep finds none either: with 1,344 or 4,032 half-hours LightGBM
  fitted on the context alone (0.510, 0.479) trails the best pretrained model (0.377, 0.360),
  though it beats Timestral 5M at 1,344. With a single day of history it beats Timestral 209M,
  Timestral 5M and t0-gamma, and only TimesFM 2.5 beats a seasonal naive that has twelve
  weeks (0.933). What limits the retail test: the data spans two years, so "long history"
  tops out at 78 weeks.
- **GB demand, 2025.** Most pretrained models also beat LightGBM fitted on a year of history
  with calendar features (0.492; 0.445 with temperature); TimesFM 2.5 (0.483) and Timestral
  5M with temperature (0.446) do not. AutoETS's automatic model selection picks a non-seasonal model on
  85 days of half-hourly demand and loses badly to seasonal naive (2.57); forcing Excel's
  ETS(A,A,A) structure fixes most of that (0.62), still behind every pretrained model and
  LightGBM.
- **GB demand after 15 Oct 2026 (leak-free).** Five days. Every pretrained model's and
  LightGBM's interval spans 1, so none is separated from seasonal naive, or from the others,
  with confidence; AutoETS is the one model reliably worse (2.28, 1.48-3.52). The order is not the
  2025 order: Chronos-2 with temperature ranks first (0.765) and LightGBM with temperature
  fifth (0.804); TimesFM 2.5 and Timestral 5M are barely ahead of seasonal naive.
- **Temperature** (an oracle daily average) helped Timestral 209M, TimesFM 3 and LightGBM a
  little in 2025 (0.357 to 0.353, 0.393 to 0.382, 0.492 to 0.445) and made Chronos-2, t0-gamma
  and Timestral 5M worse (0.373 to 0.411, 0.370 to 0.401, 0.421 to 0.446). In the five
  leak-free days it helped every model that took it except t0-gamma.
- **Promotions (FreshRetailNet).** Telling the models the planned discount, holiday and
  activity flags improved every model that took them, by 0.4% (Chronos-2) to 3.8% (TimesFM 3)
  on relative MASE; the best pretrained models with them (0.784) beat LightGBM with them
  (0.814), and Timestral 209M without them (0.805) beats LightGBM with them.
- **Calendar covariates on retail** cost Timestral 209M accuracy at the median (0.487 vs
  0.464) and wrecked its upper quantiles (see Surprises).

### Retail (UCI Online Retail II), 8 weeks ahead

| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| Timestral 209M | 1332 | 300 | 0.464 (0.42-0.52) | 0.505 | 1.065 | 0.582 | 0.82 | 0.0529 | 51293 | 611897 |
| Chronos-2 | 1332 | 300 | 0.484 (0.43-0.53) | 0.513 | 1.064 | 0.591 | 0.77 | 0.0176 | 51002 | 634129 |
| Timestral 5M | 1332 | 300 | 0.484 (0.44-0.53) | 0.509 | 1.071 | 0.587 | 0.85 | 0.0033 | 54812 | 581134 |
| TimesFM 3 (non-commercial weights) | 1332 | 300 | 0.490 (0.44-0.54) | 0.507 | 1.061 | 0.584 | 0.85 | 0.1005 | 56332 | 557426 |
| TimesFM 2.5 | 1332 | 300 | 0.498 (0.45-0.54) | 0.509 | 1.068 | 0.587 | 0.82 | 0.0610 | 78277 | 405678 |
| LightGBM (global, fitted) | 1332 | 300 | 0.540 (0.49-0.59) | 0.533 | 1.101 | 0.615 | 0.79 | 0.3732 | 91457 | 405405 |
| t0-beta | 1332 | 300 | 0.569 (0.52-0.61) | 0.530 | 1.074 | 0.611 | 0.87 | 0.0214 | 55302 | 646007 |
| t0-gamma | 1332 | 300 | 0.574 (0.53-0.62) | 0.526 | 1.081 | 0.606 | 0.88 | 0.0232 | 53859 | 651914 |
| AutoETS (spreadsheet stand-in) | 1332 | 300 | 0.741 (0.67-0.81) | 0.628 | 1.237 | 0.724 | 0.89 | 0.0932 | 55504 | 731169 |
| TSB | 1332 | 300 | 0.797 (0.74-0.85) | 0.704 | 1.203 | 0.811 | n/a | 0.0005 | n/a | n/a |
| Croston (optimised) | 1332 | 300 | 0.798 (0.74-0.86) | 0.709 | 1.231 | 0.817 | n/a | 0.0005 | n/a | n/a |
| Seasonal naive | 1332 | 300 | 1.000 (1.00-1.00) | 1.000 | 1.532 | 1.153 | n/a | 0.0003 | n/a | n/a |

### Retail, Timestral with calendar covariates

| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| Timestral 209M + calendar covariates | 1332 | 300 | 0.487 (0.44-0.54) | 0.848 | 1.078 | 0.978 | 0.85 | 0.2467 | 48569 | 3435375 |

### GB national demand, 28 days of 2025, day ahead

| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|
| Timestral 209M + temperature | 28 | 1 | 0.353 (0.28-0.44) | 0.262 | 0.433 | 0.024 | 0.87 | 2.4258 |
| Timestral 209M | 28 | 1 | 0.357 (0.29-0.44) | 0.268 | 0.440 | 0.025 | 0.89 | 0.9016 |
| t0-gamma | 28 | 1 | 0.370 (0.30-0.46) | 0.286 | 0.463 | 0.027 | 0.85 | 0.7485 |
| Chronos-2 | 28 | 1 | 0.373 (0.30-0.46) | 0.282 | 0.460 | 0.026 | 0.89 | 0.2839 |
| TimesFM 3 (non-commercial weights) + temperature | 28 | 1 | 0.382 (0.31-0.47) | 0.283 | 0.470 | 0.026 | 0.88 | 1.7080 |
| TimesFM 3 (non-commercial weights) | 28 | 1 | 0.393 (0.31-0.50) | 0.296 | 0.490 | 0.027 | 0.85 | 1.0364 |
| t0-gamma + temperature | 28 | 1 | 0.401 (0.32-0.49) | 0.297 | 0.492 | 0.028 | 0.84 | 1.9098 |
| Chronos-2 + temperature | 28 | 1 | 0.411 (0.33-0.52) | 0.305 | 0.504 | 0.028 | 0.85 | 0.4674 |
| t0-beta + temperature | 28 | 1 | 0.416 (0.33-0.52) | 0.314 | 0.515 | 0.029 | 0.85 | 1.5161 |
| t0-beta | 28 | 1 | 0.418 (0.34-0.52) | 0.322 | 0.523 | 0.030 | 0.85 | 0.8207 |
| Timestral 5M | 28 | 1 | 0.421 (0.34-0.53) | 0.318 | 0.517 | 0.030 | 0.85 | 0.0505 |
| LightGBM (global, fitted) + temperature | 28 | 1 | 0.445 (0.36-0.56) | 0.354 | 0.549 | 0.033 | 0.68 | 7.0393 |
| Timestral 5M + temperature | 28 | 1 | 0.446 (0.35-0.58) | 0.339 | 0.552 | 0.032 | 0.86 | 0.1743 |
| TimesFM 2.5 | 28 | 1 | 0.483 (0.37-0.64) | 0.367 | 0.602 | 0.034 | 0.79 | 0.8923 |
| LightGBM (global, fitted) | 28 | 1 | 0.492 (0.39-0.62) | 0.374 | 0.598 | 0.035 | 0.67 | 7.0472 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 28 | 1 | 0.617 (0.47-0.82) | 0.496 | 0.798 | 0.046 | 0.85 | 1.2151 |
| Seasonal naive | 28 | 1 | 1.000 (1.00-1.00) | 1.000 | 1.268 | 0.093 | n/a | 0.0001 |
| AutoETS (spreadsheet stand-in) | 28 | 1 | 2.565 (1.88-3.52) | 2.219 | 3.499 | 0.206 | 0.61 | 1.8767 |

### GB national demand, leak-free window (targets 15-19 Oct 2026), day ahead

| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|
| Chronos-2 + temperature | 5 | 1 | 0.765 (0.45-1.31) | 0.630 | 0.764 | 0.042 | 0.72 | 0.5763 |
| Timestral 209M + temperature | 5 | 1 | 0.779 (0.52-1.18) | 0.601 | 0.752 | 0.040 | 0.76 | 1.9316 |
| TimesFM 3 (non-commercial weights) + temperature | 5 | 1 | 0.790 (0.50-1.25) | 0.622 | 0.781 | 0.042 | 0.74 | 1.7688 |
| Timestral 209M | 5 | 1 | 0.798 (0.54-1.18) | 0.619 | 0.769 | 0.041 | 0.77 | 1.0187 |
| LightGBM (global, fitted) + temperature | 5 | 1 | 0.804 (0.59-1.09) | 0.610 | 0.743 | 0.041 | 0.67 | 6.4932 |
| LightGBM (global, fitted) | 5 | 1 | 0.847 (0.62-1.10) | 0.638 | 0.777 | 0.043 | 0.65 | 5.6993 |
| TimesFM 3 (non-commercial weights) | 5 | 1 | 0.856 (0.57-1.28) | 0.644 | 0.823 | 0.043 | 0.74 | 1.1330 |
| t0-gamma | 5 | 1 | 0.865 (0.57-1.30) | 0.666 | 0.830 | 0.044 | 0.66 | 1.0244 |
| t0-beta + temperature | 5 | 1 | 0.870 (0.54-1.39) | 0.730 | 0.867 | 0.049 | 0.76 | 1.5220 |
| t0-gamma + temperature | 5 | 1 | 0.889 (0.54-1.41) | 0.688 | 0.859 | 0.046 | 0.71 | 2.0545 |
| Chronos-2 | 5 | 1 | 0.948 (0.57-1.58) | 0.796 | 0.950 | 0.053 | 0.59 | 0.3148 |
| Timestral 5M + temperature | 5 | 1 | 0.961 (0.66-1.36) | 0.708 | 0.895 | 0.047 | 0.75 | 0.2197 |
| t0-beta | 5 | 1 | 0.965 (0.63-1.49) | 0.790 | 0.962 | 0.053 | 0.69 | 0.8164 |
| TimesFM 2.5 | 5 | 1 | 0.973 (0.57-1.53) | 0.766 | 0.940 | 0.051 | 0.66 | 1.5667 |
| Timestral 5M | 5 | 1 | 0.986 (0.65-1.43) | 0.725 | 0.921 | 0.048 | 0.73 | 0.0599 |
| Seasonal naive | 5 | 1 | 1.000 (1.00-1.00) | 1.000 | 0.947 | 0.067 | n/a | 0.0003 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 5 | 1 | 1.088 (0.68-1.69) | 0.908 | 1.083 | 0.061 | 0.72 | 1.1408 |
| AutoETS (spreadsheet stand-in) | 5 | 1 | 2.284 (1.48-3.52) | 1.817 | 2.201 | 0.121 | 0.67 | 2.4376 |

### FreshRetailNet-50K, 7 days ahead, with and without the planned discount

| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| TimesFM 3 (non-commercial weights) + discount, holiday, activity | 400 | 400 | 0.784 (0.76-0.81) | 0.624 | 0.964 | 0.264 | 0.78 | 0.1755 | 126 | 1748 |
| t0-gamma + discount, holiday, activity | 400 | 400 | 0.784 (0.75-0.82) | 0.632 | 0.966 | 0.268 | 0.78 | 0.0903 | 138 | 1805 |
| Timestral 209M + discount, holiday, activity | 400 | 400 | 0.793 (0.76-0.82) | 0.637 | 0.974 | 0.270 | 0.78 | 0.1293 | 130 | 1866 |
| Timestral 209M | 400 | 400 | 0.805 (0.78-0.83) | 0.641 | 0.987 | 0.272 | 0.77 | 0.0205 | 123 | 1846 |
| Chronos-2 + discount, holiday, activity | 400 | 400 | 0.808 (0.78-0.84) | 0.649 | 0.996 | 0.275 | 0.74 | 0.0364 | 168 | 1641 |
| t0-gamma | 400 | 400 | 0.808 (0.78-0.84) | 0.647 | 0.992 | 0.274 | 0.78 | 0.0410 | 118 | 1958 |
| Chronos-2 | 400 | 400 | 0.811 (0.78-0.84) | 0.652 | 1.004 | 0.277 | 0.76 | 0.0126 | 130 | 1831 |
| LightGBM (global, fitted) + discount, holiday, activity | 400 | 400 | 0.814 (0.79-0.84) | 0.678 | 1.017 | 0.287 | 0.73 | 0.0513 | 228 | 1612 |
| TimesFM 3 (non-commercial weights) | 400 | 400 | 0.815 (0.79-0.85) | 0.651 | 1.003 | 0.276 | 0.78 | 0.0409 | 125 | 1935 |
| LightGBM (global, fitted) | 400 | 400 | 0.833 (0.81-0.86) | 0.692 | 1.034 | 0.293 | 0.74 | 0.0330 | 219 | 1694 |
| AutoETS (spreadsheet stand-in) | 400 | 400 | 0.851 (0.82-0.88) | 0.683 | 1.026 | 0.290 | 0.73 | 0.0870 | 159 | 1798 |
| Seasonal naive | 400 | 400 | 1.000 (1.00-1.00) | 1.000 | 1.199 | 0.424 | n/a | 0.0001 | n/a | n/a |

### History-length sweep (retail_sweep, weeks; 342 windows, 80 series)

Relative MASE (geometric mean) / relative WQL (pooled) / mean MASE; seasonal naive with the longest history = 1 for the two relative figures:

| Model | L=8 | L=13 | L=26 | L=52 | L=78 |
|---|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | 0.662 / 8.240 / 1.248 | 0.667 / 0.688 / 1.291 | 0.658 / 0.744 / 1.356 | 0.672 / 0.656 / 1.245 | 0.753 / 0.698 / 1.302 |
| Chronos-2 | 0.381 / 0.592 / 1.173 | 0.515 / 0.591 / 1.122 | 0.484 / 0.614 / 1.091 | 0.475 / 0.540 / 1.083 | 0.476 / 0.549 / 1.085 |
| LightGBM (global, fitted) | 0.631 / 0.644 / 1.334 | 0.570 / 0.600 / 1.205 | 0.559 / 0.631 / 1.194 | 0.533 / 0.574 / 1.127 | 0.599 / 0.564 / 1.173 |
| Seasonal naive | 0.622 / 0.785 / 1.233 | 0.622 / 0.785 / 1.233 | 0.622 / 0.785 / 1.233 | 1.000 / 1.000 / 1.587 | 1.000 / 1.000 / 1.587 |
| t0-gamma | 0.574 / 0.595 / 1.129 | 0.547 / 0.607 / 1.097 | 0.542 / 0.612 / 1.084 | 0.519 / 0.533 / 1.086 | 0.527 / 0.555 / 1.116 |
| TimesFM 2.5 | 0.523 / 0.585 / 1.097 | 0.465 / 0.621 / 1.103 | 0.489 / 0.625 / 1.108 | 0.484 / 0.560 / 1.089 | 0.518 / 0.563 / 1.107 |
| TimesFM 3 (non-commercial weights) | 0.554 / 0.590 / 1.140 | 0.461 / 0.603 / 1.100 | 0.472 / 0.816 / 1.170 | 0.468 / 0.531 / 1.076 | 0.501 / 0.548 / 1.113 |
| Timestral 209M | 0.558 / 0.585 / 1.128 | 0.491 / 0.596 / 1.101 | 0.462 / 0.596 / 1.070 | 0.446 / 0.546 / 1.067 | 0.457 / 0.536 / 1.073 |
| Timestral 5M | 0.542 / 0.594 / 1.116 | 0.481 / 0.605 / 1.110 | 0.495 / 0.599 / 1.077 | 0.443 / 0.555 / 1.079 | 0.469 / 0.548 / 1.083 |

### History-length sweep (grid_sweep, half-hours; 12 windows, 1 series)

Relative MASE (geometric mean) / relative WQL (pooled) / mean MASE; seasonal naive with the longest history = 1 for the two relative figures:

| Model | L=48 | L=336 | L=1344 | L=4032 |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | 3.215 / 3.994 / 5.534 | 2.511 / 2.227 / 3.457 | 2.523 / 2.308 / 3.501 | 2.646 / 2.371 / 3.573 |
| Chronos-2 | 1.355 / 1.099 / 1.699 | 0.604 / 0.550 / 0.814 | 0.410 / 0.349 / 0.535 | 0.369 / 0.294 / 0.456 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 3.128 / 3.813 / 5.457 | 0.789 / 0.897 / 1.281 | 0.704 / 0.629 / 0.967 | 0.699 / 0.615 / 0.951 |
| LightGBM (fitted on the context only) | 1.422 / 1.056 / 1.632 | 0.667 / 0.637 / 0.872 | 0.510 / 0.427 / 0.620 | 0.479 / 0.396 / 0.590 |
| Seasonal naive | 1.869 / 1.902 / 2.269 | 1.000 / 1.000 / 1.217 | 1.000 / 1.000 / 1.217 | 1.000 / 1.000 / 1.217 |
| t0-gamma | 1.783 / 1.417 / 2.194 | 0.498 / 0.434 / 0.657 | 0.377 / 0.305 / 0.462 | 0.389 / 0.308 / 0.476 |
| TimesFM 2.5 | 0.933 / 0.796 / 1.218 | 0.525 / 0.408 / 0.643 | 0.488 / 0.398 / 0.613 | 0.449 / 0.356 / 0.553 |
| TimesFM 3 (non-commercial weights) | 1.163 / 1.009 / 1.498 | 0.473 / 0.395 / 0.604 | 0.399 / 0.319 / 0.491 | 0.397 / 0.313 / 0.492 |
| Timestral 209M | 1.644 / 1.282 / 2.012 | 0.462 / 0.444 / 0.629 | 0.399 / 0.338 / 0.506 | 0.360 / 0.280 / 0.438 |
| Timestral 5M | 1.550 / 1.223 / 1.850 | 0.597 / 0.543 / 0.820 | 0.535 / 0.438 / 0.664 | 0.446 / 0.357 / 0.543 |

![History-length sweep, retail](charts/sweep_retail.svg)

![History-length sweep, GB demand](charts/sweep_grid.svg)

![One product's forecasts](charts/example_forecast.svg)

The example product is chosen by rule (the highest-volume product with all five cut-offs), not
picked for the result; on it LightGBM's band fits best. `results/demo.json` holds twelve
rule-picked products (`charts/demo_picks.json`) and both grid windows for the article's
interactive chart.

### Calibration and ordering at the 90th percentile (retail)

Over all 1,332 retail windows, customers bought 362,575 units. Ordering each week at a model's
90th percentile leaves between 51,002 (Chronos-2) and 91,457 (LightGBM) units short and
between 405,405 (LightGBM) and 731,169 (AutoETS) units over. The pretrained models'
10-90% bands cover 0.77-0.88 of actuals; LightGBM's 0.79; AutoETS's 0.89. The grid bands of
LightGBM (0.67-0.68) and AutoETS (0.61) are too narrow; the pretrained models' cover 0.79-0.89
in 2025 and 0.59-0.77 in the five leak-free days.

### Surprises and doubts

- **A cancelled order is in the raw data as a sale.** Dropping cancellation lines alone, as
  the usual cleaning recipe says, leaves 74,215 storage jars ordered and cancelled on
  18 January 2011 as a real sale, and that one spike dominated the first run's stock-out
  figures. The cleaning now drops the originals that cancellations reverse.
- **A known-future flag the model has never seen switched on blows up Timestral's upper
  quantiles.** With a Nov-Dec flag that is zero throughout a 29-week history and one in the
  last five forecast weeks, Timestral 209M's median stays sensible (26-62 units) but its 90th
  percentile reaches 327,000 units a week (`results/sanity.json`, product 23155). Without the
  covariate the 90th percentile is 73-92. That is why the calendar row's WQL is 0.978.
- **AutoETS is not a seasonal model here.** With under two years of weekly data it chose a
  non-seasonal model for 19 of the 20 longest retail histories, and on half-hourly demand it
  chose (A,A,N) or (M,A,N) over the seasonal (A,A,A) on every window checked. Excel's
  `FORECAST.ETS` detects and fits seasonality itself, so the ETS(A,A,A) row is the closer
  stand-in on the grid. Neither is Excel's code.
- **Geometric and arithmetic means disagree on retail.** The geometric mean of per-window
  ratios (the GIFT-Eval aggregate) puts the pretrained models about 50% ahead of seasonal
  naive; the mean MASE puts them about 30% ahead (1.06 against 1.53), because many intermittent
  windows have small absolute errors that dominate a geometric mean. The ranking among models
  barely changes; Chronos-2's lead at 8 weeks in the sweep is a geometric-mean effect (its
  mean MASE there is the worst of the pretrained models).
- **Chronos-2's raw quantiles cross** on 490 retail (window, step) pairs; all quantiles are
  sorted before scoring, for every model.
- **Leakage.** Online Retail II and NESO's historic demand are old and public, and the
  pretraining corpora of these models (GIFT-Eval pretraining data, Chronos datasets, synthetic
  data) may contain either. Nothing here shows they do not. The leak-free window is the only
  answer, and with five days it is too small to rank the models.
- **Sample sizes.** 300 of 3,295 eligible products; 28 grid days; 5 leak-free days; 12 grid
  sweep days. The retail intervals are tight enough to separate the pack from AutoETS, not
  the pretrained models from each other.

### Timing

Times are wall-clock on a machine other jobs were using: the 1-minute load average during the
runs ranged from about 11 to 218 on 8 cores (`loadavg_1min_before` in `results/summary.json`).
Treat them as indicative and as ratios, not absolutes.

The quieter pass below (`scripts/timing.py`, `results/timing_*.json`) ran after the backtest
with the 1-minute load average between 1.6 and 3.2: 256 retail windows and the 5 leak-free
grid windows (4,096 steps of context), no covariates, median of three repeats. These are the
better numbers to quote; still indicative.

| Model | Retail, ms per series | Grid, s per day-ahead forecast | Load, s |
|---|---|---|---|
| Timestral 5M | 0.5 | 0.01 | 0.1 |
| Timestral 209M | 6.1 | 0.16 | 1.8 |
| Chronos-2 | 2.2 | 0.08 | 0.1 |
| TimesFM 2.5 | 6.8 | 0.29 | 4.8 |
| TimesFM 3 (non-commercial weights) | 11.2 | 0.29 | 5.2 |
| t0-gamma | 5.5 | 0.24 | 2.8 |
| AutoETS (spreadsheet stand-in) | 21.4 | 2.71 | 0.0 |
| LightGBM (global, fitted) | 84.1 | 2.77 | 0.0 |

AutoETS and LightGBM times include fitting; LightGBM retail fits 72 models (9 quantiles x 8
horizons) on the 256 series' histories. The pretrained models' load time is reading the
weights from the local cache.

The backtest's own timings, under heavy load:


| Model | Retail, s per window (1,332) | Grid, s per window (28, 4,096 steps) | Load (s) |
|---|---|---|---|
| Seasonal naive | 0.0003 | 0.0001 |  |
| Croston (optimised) | 0.0005 | n/a |  |
| TSB | 0.0005 | n/a |  |
| AutoETS (spreadsheet stand-in) | 0.0932 | 1.8767 |  |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | n/a | 1.2151 |  |
| LightGBM (global, fitted) | 0.3732 | 7.0472 |  |
| Timestral 5M | 0.0033 | 0.0505 | 0.3 |
| Timestral 209M | 0.0529 | 0.9016 | 4.5 |
| Chronos-2 | 0.0176 | 0.2839 | 0.3 |
| TimesFM 2.5 | 0.0610 | 0.8923 | 6.9 |
| TimesFM 3 (non-commercial weights) | 0.1005 | 1.0364 | 8.3 |
| t0-gamma | 0.0232 | 0.7485 | 4.3 |
| t0-beta | 0.0214 | 0.8207 | 3.3 |

AutoETS on the grid ran in 8 worker processes and LightGBM on one thread (faster than eight on
this busy machine: 1.9 s against 4.9 s for one 25,000-row fit). The pretrained models'
default symmetric averaging (Timestral, TimesFM 3, t0) runs each forecast twice.



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
uv run python scripts/timing.py --family neural    # optional quiet-machine timing pass
uv run python scripts/timing.py --family classical
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

Output on 20 October 2026 (Timestral-209M at commit `a534bdb`, CPU):

```text
              p10  median     p90  actual
ds                                       
2011-10-16  128.0   415.0  1062.0   683.0
2011-10-23  139.0   488.0  1215.0   234.0
2011-10-30  154.0   514.0  1273.0   447.0
2011-11-06  148.0   535.0  1320.0  1706.0
2011-11-13  151.0   540.0  1327.0   594.0
2011-11-20  146.0   538.0  1341.0  1326.0
2011-11-27  140.0   530.0  1346.0   904.0
2011-12-04  141.0   534.0  1361.0   731.0
```

Seven of the eight actuals (234 to 1,706 units a week) fall inside the 10-90% band; the 1,706-unit week is above it.

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
from the 34,074 whose discount changes during the evaluation week, so a model that is told the
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
| AutoETS | `statsforecast` 2.1.1 `AutoETS`, season 52 (retail), 48 (grid), 7 (FreshRetailNet); automatic model selection; intervals from the model at 20/40/60/80% give the nine quantiles. A stand-in for Excel's `FORECAST.ETS`, which fits an additive (AAA) ETS model: not the same code. With at most 96 weeks of weekly history it chose a non-seasonal model for 19 of the 20 longest retail histories; on the grid it chose non-seasonal models on 85 days of half-hourly data, so ETS(A,A,A) is also run there (`results/sanity.json`). |
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

