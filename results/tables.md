### Retail (UCI Online Retail II), 8 weeks ahead

| Model | Windows | Series | Mean-MASE ratio (95% CI) | Geo. rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TimesFM 3 (non-commercial weights) | 1332 | 300 | 0.692 (0.64-0.75) | 0.490 (0.44-0.54) | 0.507 | 1.061 | 0.584 | 0.85 | 0.1005 | 56332 | 557426 |
| Chronos-2 | 1332 | 300 | 0.695 (0.64-0.75) | 0.484 (0.43-0.53) | 0.513 | 1.064 | 0.591 | 0.77 | 0.0176 | 51002 | 634129 |
| Timestral 209M | 1332 | 300 | 0.696 (0.64-0.75) | 0.464 (0.42-0.52) | 0.505 | 1.065 | 0.582 | 0.82 | 0.0529 | 51293 | 611897 |
| TimesFM 2.5 | 1332 | 300 | 0.697 (0.64-0.75) | 0.498 (0.45-0.54) | 0.509 | 1.068 | 0.587 | 0.82 | 0.0610 | 78277 | 405678 |
| Timestral 5M | 1332 | 300 | 0.699 (0.64-0.75) | 0.484 (0.44-0.53) | 0.509 | 1.071 | 0.587 | 0.85 | 0.0033 | 54812 | 581134 |
| t0-beta | 1332 | 300 | 0.701 (0.65-0.75) | 0.569 (0.52-0.61) | 0.530 | 1.074 | 0.611 | 0.87 | 0.0214 | 55302 | 646007 |
| t0-gamma | 1332 | 300 | 0.706 (0.65-0.76) | 0.574 (0.53-0.62) | 0.526 | 1.081 | 0.606 | 0.88 | 0.0232 | 53859 | 651914 |
| LightGBM (global, fitted) | 1332 | 300 | 0.719 (0.66-0.77) | 0.540 (0.49-0.59) | 0.533 | 1.101 | 0.615 | 0.79 | 0.3732 | 91457 | 405405 |
| TSB | 1332 | 300 | 0.785 (0.74-0.84) | 0.797 (0.74-0.85) | 0.704 | 1.203 | 0.811 | n/a | 0.0005 | n/a | n/a |
| Croston (optimised) | 1332 | 300 | 0.803 (0.75-0.85) | 0.798 (0.74-0.86) | 0.709 | 1.231 | 0.817 | n/a | 0.0005 | n/a | n/a |
| AutoETS (spreadsheet stand-in) | 1332 | 300 | 0.808 (0.76-0.86) | 0.741 (0.67-0.81) | 0.628 | 1.237 | 0.724 | 0.89 | 0.0932 | 55504 | 731169 |
| Seasonal naive | 1332 | 300 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) | 1.000 | 1.532 | 1.153 | n/a | 0.0003 | n/a | n/a |

### Retail, Timestral with calendar covariates

| Model | Windows | Series | Mean-MASE ratio (95% CI) | Geo. rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Timestral 209M + calendar covariates | 1332 | 300 | 0.704 (0.65-0.76) | 0.487 (0.44-0.54) | 0.848 | 1.078 | 0.978 | 0.85 | 0.2467 | 48569 | 3435375 |

### GB national demand, 28 days of 2025, day ahead

| Model | Windows | Series | Geo. rel. MASE (95% CI) | Mean-MASE ratio (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|---|
| Timestral 209M + temperature | 28 | 1 | 0.353 (0.28-0.44) | 0.342 (0.27-0.43) | 0.262 | 0.433 | 0.024 | 0.87 | 2.4258 |
| Timestral 209M | 28 | 1 | 0.357 (0.29-0.44) | 0.347 (0.28-0.43) | 0.268 | 0.440 | 0.025 | 0.89 | 0.9016 |
| t0-gamma | 28 | 1 | 0.370 (0.30-0.46) | 0.365 (0.30-0.45) | 0.286 | 0.463 | 0.027 | 0.85 | 0.7485 |
| Chronos-2 | 28 | 1 | 0.373 (0.30-0.46) | 0.363 (0.29-0.46) | 0.282 | 0.460 | 0.026 | 0.89 | 0.2839 |
| TimesFM 3 (non-commercial weights) + temperature | 28 | 1 | 0.382 (0.31-0.47) | 0.371 (0.30-0.46) | 0.283 | 0.470 | 0.026 | 0.88 | 1.7080 |
| TimesFM 3 (non-commercial weights) | 28 | 1 | 0.393 (0.31-0.50) | 0.386 (0.31-0.48) | 0.296 | 0.490 | 0.027 | 0.85 | 1.0364 |
| t0-gamma + temperature | 28 | 1 | 0.401 (0.32-0.49) | 0.388 (0.31-0.48) | 0.297 | 0.492 | 0.028 | 0.84 | 1.9098 |
| Chronos-2 + temperature | 28 | 1 | 0.411 (0.33-0.52) | 0.398 (0.32-0.50) | 0.305 | 0.504 | 0.028 | 0.85 | 0.4674 |
| t0-beta + temperature | 28 | 1 | 0.416 (0.33-0.52) | 0.406 (0.33-0.50) | 0.314 | 0.515 | 0.029 | 0.85 | 1.5161 |
| t0-beta | 28 | 1 | 0.418 (0.34-0.52) | 0.412 (0.33-0.50) | 0.322 | 0.523 | 0.030 | 0.85 | 0.8207 |
| Timestral 5M | 28 | 1 | 0.421 (0.34-0.53) | 0.407 (0.32-0.51) | 0.318 | 0.517 | 0.030 | 0.85 | 0.0505 |
| LightGBM (global, fitted) + temperature | 28 | 1 | 0.445 (0.36-0.56) | 0.433 (0.35-0.53) | 0.354 | 0.549 | 0.033 | 0.68 | 7.0393 |
| Timestral 5M + temperature | 28 | 1 | 0.446 (0.35-0.58) | 0.435 (0.34-0.56) | 0.339 | 0.552 | 0.032 | 0.86 | 0.1743 |
| TimesFM 2.5 | 28 | 1 | 0.483 (0.37-0.64) | 0.475 (0.37-0.63) | 0.367 | 0.602 | 0.034 | 0.79 | 0.8923 |
| LightGBM (global, fitted) | 28 | 1 | 0.492 (0.39-0.62) | 0.472 (0.39-0.58) | 0.374 | 0.598 | 0.035 | 0.67 | 7.0472 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 28 | 1 | 0.617 (0.47-0.82) | 0.629 (0.47-0.83) | 0.496 | 0.798 | 0.046 | 0.85 | 1.2151 |
| Seasonal naive | 28 | 1 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) | 1.000 | 1.268 | 0.093 | n/a | 0.0001 |
| AutoETS (spreadsheet stand-in) | 28 | 1 | 2.565 (1.88-3.52) | 2.759 (2.08-3.64) | 2.219 | 3.499 | 0.206 | 0.61 | 1.8767 |

### GB national demand, leak-free window (targets 15-19 Oct 2026), day ahead

| Model | Windows | Series | Geo. rel. MASE (95% CI) | Mean-MASE ratio (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|---|
| Chronos-2 + temperature | 5 | 1 | 0.765 (0.45-1.31) | 0.807 (0.43-1.34) | 0.630 | 0.764 | 0.042 | 0.72 | 0.5763 |
| Timestral 209M + temperature | 5 | 1 | 0.779 (0.52-1.18) | 0.794 (0.50-1.21) | 0.601 | 0.752 | 0.040 | 0.76 | 1.9316 |
| TimesFM 3 (non-commercial weights) + temperature | 5 | 1 | 0.790 (0.50-1.25) | 0.825 (0.48-1.31) | 0.622 | 0.781 | 0.042 | 0.74 | 1.7688 |
| Timestral 209M | 5 | 1 | 0.798 (0.54-1.18) | 0.813 (0.53-1.22) | 0.619 | 0.769 | 0.041 | 0.77 | 1.0187 |
| LightGBM (global, fitted) + temperature | 5 | 1 | 0.804 (0.59-1.09) | 0.784 (0.56-1.10) | 0.610 | 0.743 | 0.041 | 0.67 | 6.4932 |
| LightGBM (global, fitted) | 5 | 1 | 0.847 (0.62-1.10) | 0.820 (0.62-1.11) | 0.638 | 0.777 | 0.043 | 0.65 | 5.6993 |
| TimesFM 3 (non-commercial weights) | 5 | 1 | 0.856 (0.57-1.28) | 0.869 (0.55-1.32) | 0.644 | 0.823 | 0.043 | 0.74 | 1.1330 |
| t0-gamma | 5 | 1 | 0.865 (0.57-1.30) | 0.877 (0.56-1.33) | 0.666 | 0.830 | 0.044 | 0.66 | 1.0244 |
| t0-beta + temperature | 5 | 1 | 0.870 (0.54-1.39) | 0.916 (0.52-1.49) | 0.730 | 0.867 | 0.049 | 0.76 | 1.5220 |
| t0-gamma + temperature | 5 | 1 | 0.889 (0.54-1.41) | 0.907 (0.57-1.42) | 0.688 | 0.859 | 0.046 | 0.71 | 2.0545 |
| Chronos-2 | 5 | 1 | 0.948 (0.57-1.58) | 1.004 (0.56-1.63) | 0.796 | 0.950 | 0.053 | 0.59 | 0.3148 |
| Timestral 5M + temperature | 5 | 1 | 0.961 (0.66-1.36) | 0.945 (0.65-1.38) | 0.708 | 0.895 | 0.047 | 0.75 | 0.2197 |
| t0-beta | 5 | 1 | 0.965 (0.63-1.49) | 1.016 (0.60-1.60) | 0.790 | 0.962 | 0.053 | 0.69 | 0.8164 |
| TimesFM 2.5 | 5 | 1 | 0.973 (0.57-1.53) | 0.993 (0.62-1.52) | 0.766 | 0.940 | 0.051 | 0.66 | 1.5667 |
| Timestral 5M | 5 | 1 | 0.986 (0.65-1.43) | 0.973 (0.65-1.44) | 0.725 | 0.921 | 0.048 | 0.73 | 0.0599 |
| Seasonal naive | 5 | 1 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) | 1.000 | 0.947 | 0.067 | n/a | 0.0003 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 5 | 1 | 1.088 (0.68-1.69) | 1.144 (0.69-1.78) | 0.908 | 1.083 | 0.061 | 0.72 | 1.1408 |
| AutoETS (spreadsheet stand-in) | 5 | 1 | 2.284 (1.48-3.52) | 2.324 (1.42-3.61) | 1.817 | 2.201 | 0.121 | 0.67 | 2.4376 |

### FreshRetailNet-50K, 7 days ahead, with and without the planned discount

| Model | Windows | Series | Mean-MASE ratio (95% CI) | Geo. rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window | Units short @p90 | Units over @p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TimesFM 3 (non-commercial weights) + discount, holiday, activity | 400 | 400 | 0.804 (0.78-0.83) | 0.784 (0.76-0.81) | 0.624 | 0.964 | 0.264 | 0.78 | 0.1755 | 126 | 1748 |
| t0-gamma + discount, holiday, activity | 400 | 400 | 0.805 (0.78-0.84) | 0.784 (0.75-0.82) | 0.632 | 0.966 | 0.268 | 0.78 | 0.0903 | 138 | 1805 |
| Timestral 209M + discount, holiday, activity | 400 | 400 | 0.813 (0.78-0.85) | 0.793 (0.76-0.82) | 0.637 | 0.974 | 0.270 | 0.78 | 0.1293 | 130 | 1866 |
| Timestral 209M | 400 | 400 | 0.823 (0.80-0.85) | 0.805 (0.78-0.83) | 0.641 | 0.987 | 0.272 | 0.77 | 0.0205 | 123 | 1846 |
| t0-gamma | 400 | 400 | 0.827 (0.80-0.86) | 0.808 (0.78-0.84) | 0.647 | 0.992 | 0.274 | 0.78 | 0.0410 | 118 | 1958 |
| Chronos-2 + discount, holiday, activity | 400 | 400 | 0.831 (0.80-0.87) | 0.808 (0.78-0.84) | 0.649 | 0.996 | 0.275 | 0.74 | 0.0364 | 168 | 1641 |
| TimesFM 3 (non-commercial weights) | 400 | 400 | 0.836 (0.81-0.87) | 0.815 (0.79-0.85) | 0.651 | 1.003 | 0.276 | 0.78 | 0.0409 | 125 | 1935 |
| Chronos-2 | 400 | 400 | 0.837 (0.81-0.87) | 0.811 (0.78-0.84) | 0.652 | 1.004 | 0.277 | 0.76 | 0.0126 | 130 | 1831 |
| LightGBM (global, fitted) + discount, holiday, activity | 400 | 400 | 0.848 (0.81-0.89) | 0.814 (0.79-0.84) | 0.678 | 1.017 | 0.287 | 0.73 | 0.0513 | 228 | 1612 |
| AutoETS (spreadsheet stand-in) | 400 | 400 | 0.855 (0.83-0.88) | 0.851 (0.82-0.88) | 0.683 | 1.026 | 0.290 | 0.73 | 0.0870 | 159 | 1798 |
| LightGBM (global, fitted) | 400 | 400 | 0.862 (0.83-0.90) | 0.833 (0.81-0.86) | 0.692 | 1.034 | 0.293 | 0.74 | 0.0330 | 219 | 1694 |
| Seasonal naive | 400 | 400 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) | 1.000 | 1.199 | 0.424 | n/a | 0.0001 | n/a | n/a |

### History-length sweep (retail_sweep, weeks; 342 windows, 80 series)

Mean-MASE ratio / relative WQL (pooled) / geometric-mean relative MASE; seasonal naive with the longest history = 1:

| Model | L=8 | L=13 | L=26 | L=52 | L=78 |
|---|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | 0.786 / 8.240 / 0.662 | 0.813 / 0.688 / 0.667 | 0.854 / 0.744 / 0.658 | 0.785 / 0.656 / 0.672 | 0.821 / 0.698 / 0.753 |
| Chronos-2 | 0.739 / 0.592 / 0.381 | 0.707 / 0.591 / 0.515 | 0.687 / 0.614 / 0.484 | 0.682 / 0.540 / 0.475 | 0.683 / 0.549 / 0.476 |
| LightGBM (global, fitted) | 0.841 / 0.644 / 0.631 | 0.759 / 0.600 / 0.570 | 0.752 / 0.631 / 0.559 | 0.710 / 0.574 / 0.533 | 0.739 / 0.564 / 0.599 |
| Seasonal naive | 0.777 / 0.785 / 0.622 | 0.777 / 0.785 / 0.622 | 0.777 / 0.785 / 0.622 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 |
| t0-gamma | 0.711 / 0.595 / 0.574 | 0.691 / 0.607 / 0.547 | 0.683 / 0.612 / 0.542 | 0.684 / 0.533 / 0.519 | 0.703 / 0.555 / 0.527 |
| TimesFM 2.5 | 0.691 / 0.585 / 0.523 | 0.695 / 0.621 / 0.465 | 0.698 / 0.625 / 0.489 | 0.686 / 0.560 / 0.484 | 0.698 / 0.563 / 0.518 |
| TimesFM 3 (non-commercial weights) | 0.719 / 0.590 / 0.554 | 0.693 / 0.603 / 0.461 | 0.737 / 0.816 / 0.472 | 0.678 / 0.531 / 0.468 | 0.701 / 0.548 / 0.501 |
| Timestral 209M | 0.710 / 0.585 / 0.558 | 0.694 / 0.596 / 0.491 | 0.674 / 0.596 / 0.462 | 0.672 / 0.546 / 0.446 | 0.676 / 0.536 / 0.457 |
| Timestral 5M | 0.703 / 0.594 / 0.542 | 0.699 / 0.605 / 0.481 | 0.678 / 0.599 / 0.495 | 0.680 / 0.555 / 0.443 | 0.682 / 0.548 / 0.469 |

### History-length sweep (grid_sweep, half-hours; 12 windows, 1 series)

Geometric-mean relative MASE / relative WQL (pooled) / mean-MASE ratio; seasonal naive with the longest history = 1:

| Model | L=48 | L=336 | L=1344 | L=4032 |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | 3.215 / 3.994 / 4.549 | 2.511 / 2.227 / 2.842 | 2.523 / 2.308 / 2.877 | 2.646 / 2.371 / 2.937 |
| Chronos-2 | 1.355 / 1.099 / 1.396 | 0.604 / 0.550 / 0.669 | 0.410 / 0.349 / 0.439 | 0.369 / 0.294 / 0.375 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 3.128 / 3.813 / 4.486 | 0.789 / 0.897 / 1.053 | 0.704 / 0.629 / 0.795 | 0.699 / 0.615 / 0.782 |
| LightGBM (fitted on the context only) | 1.422 / 1.056 / 1.341 | 0.667 / 0.637 / 0.716 | 0.510 / 0.427 / 0.509 | 0.479 / 0.396 / 0.485 |
| Seasonal naive | 1.869 / 1.902 / 1.865 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 |
| t0-gamma | 1.783 / 1.417 / 1.804 | 0.498 / 0.434 / 0.540 | 0.377 / 0.305 / 0.380 | 0.389 / 0.308 / 0.391 |
| TimesFM 2.5 | 0.933 / 0.796 / 1.001 | 0.525 / 0.408 / 0.529 | 0.488 / 0.398 / 0.504 | 0.449 / 0.356 / 0.455 |
| TimesFM 3 (non-commercial weights) | 1.163 / 1.009 / 1.231 | 0.473 / 0.395 / 0.497 | 0.399 / 0.319 / 0.404 | 0.397 / 0.313 / 0.404 |
| Timestral 209M | 1.644 / 1.282 / 1.654 | 0.462 / 0.444 / 0.517 | 0.399 / 0.338 / 0.416 | 0.360 / 0.280 / 0.360 |
| Timestral 5M | 1.550 / 1.223 / 1.521 | 0.597 / 0.543 / 0.674 | 0.535 / 0.438 / 0.546 | 0.446 / 0.357 / 0.447 |

### GB demand floor sweep: 28 day-ahead forecasts across 2025, same targets at every length (N = 28 windows per length)

Geometric-mean relative MASE (95% CI), baseline = seasonal naive with the longest history:

| Model | 12 half-hours | 24 half-hours | 48 half-hours | 96 half-hours | 144 half-hours | 336 half-hours |
|---|---|---|---|---|---|---|
| Chronos-2 | 2.515 (1.66-3.87) | 1.726 (1.24-2.45) | 1.389 (1.03-1.92) | 0.638 (0.48-0.85) | 0.680 (0.49-0.94) | 0.526 (0.40-0.70) |
| Chronos-2 + temperature | 2.582 (1.61-4.21) | 1.862 (1.32-2.71) | 1.219 (0.88-1.74) | 0.726 (0.51-1.04) | 0.690 (0.51-0.94) | 0.561 (0.41-0.75) |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | cannot fit | cannot fit | cannot fit | 0.889 (0.64-1.22) | 0.727 (0.53-1.01) | 0.677 (0.48-0.96) |
| LightGBM (fitted on the context only) | cannot fit | cannot fit | 1.331 (1.08-1.66) | 0.803 (0.62-1.05) | 0.656 (0.50-0.85) | 0.613 (0.47-0.79) |
| LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit | 1.331 (1.08-1.66) | 0.808 (0.62-1.05) | 0.661 (0.50-0.86) | 0.643 (0.48-0.85) |
| Seasonal naive | 1.848 (1.43-2.44) | 1.848 (1.43-2.44) | 0.561 (0.42-0.75) | 0.561 (0.42-0.75) | 0.561 (0.42-0.75) | 1.000 (1.00-1.00) |
| t0-beta | 1.785 (1.31-2.56) | 1.428 (1.11-1.88) | 1.468 (1.11-1.97) | 1.000 (0.71-1.38) | 0.740 (0.54-1.01) | 0.528 (0.40-0.70) |
| t0-beta + temperature | 1.966 (1.30-3.01) | 1.600 (1.19-2.21) | 1.651 (1.20-2.31) | 1.642 (1.25-2.22) | 1.036 (0.70-1.51) | 0.635 (0.47-0.85) |
| t0-gamma | 3.409 (2.58-4.66) | 1.932 (1.50-2.50) | 1.655 (1.26-2.25) | 0.684 (0.49-0.95) | 0.567 (0.41-0.78) | 0.454 (0.35-0.58) |
| t0-gamma + temperature | 2.918 (2.25-3.87) | 1.802 (1.41-2.34) | 1.643 (1.25-2.20) | 0.682 (0.47-0.98) | 0.555 (0.40-0.75) | 0.462 (0.35-0.59) |
| Theory model, fitted on the context + temperature | 2.027 (1.67-2.45) | 1.674 (1.37-2.08) | 0.693 (0.54-0.89) | 0.582 (0.44-0.77) | 0.644 (0.47-0.87) | 0.617 (0.48-0.78) |
| Theory model, structure from 2024 + temperature | 0.614 (0.47-0.78) | 0.655 (0.48-0.86) | 0.616 (0.46-0.79) | 0.639 (0.49-0.82) | 0.610 (0.45-0.79) | 0.637 (0.48-0.82) |
| TimesFM 2.5 | 1.631 (1.28-2.08) | 1.242 (0.98-1.60) | 0.750 (0.58-0.99) | 0.649 (0.49-0.86) | 0.546 (0.41-0.74) | 0.512 (0.41-0.64) |
| TimesFM 3 (non-commercial weights) | 3.534 (2.15-5.85) | 1.844 (1.33-2.65) | 1.011 (0.73-1.39) | 0.552 (0.42-0.73) | 0.526 (0.41-0.68) | 0.452 (0.36-0.58) |
| TimesFM 3 (non-commercial weights) + temperature | 3.926 (2.50-6.29) | 1.784 (1.28-2.53) | 1.654 (1.23-2.28) | 0.583 (0.44-0.76) | 0.515 (0.40-0.68) | 0.454 (0.35-0.59) |
| Timestral 209M | 3.140 (2.04-4.87) | 1.604 (1.19-2.21) | 1.524 (1.16-2.05) | 0.514 (0.38-0.69) | 0.517 (0.39-0.69) | 0.436 (0.33-0.56) |
| Timestral 209M + temperature | 2.861 (2.06-4.06) | 1.772 (1.29-2.48) | 1.806 (1.34-2.47) | 0.537 (0.39-0.73) | 0.518 (0.38-0.70) | 0.480 (0.36-0.64) |
| Timestral 5M | 2.974 (2.02-4.48) | 1.533 (1.16-2.08) | 1.482 (1.15-1.95) | 0.677 (0.50-0.91) | 0.598 (0.44-0.80) | 0.506 (0.37-0.68) |
| Timestral 5M + temperature | 2.893 (2.03-4.20) | 1.591 (1.21-2.16) | 1.713 (1.33-2.26) | 0.792 (0.57-1.08) | 0.617 (0.44-0.84) | 0.553 (0.40-0.75) |

Mean-MASE ratio (95% CI), baseline = seasonal naive with the longest history:

| Model | 12 half-hours | 24 half-hours | 48 half-hours | 96 half-hours | 144 half-hours | 336 half-hours |
|---|---|---|---|---|---|---|
| Chronos-2 | 3.409 (2.36-4.63) | 1.944 (1.39-2.67) | 1.420 (1.06-1.94) | 0.663 (0.50-0.88) | 0.741 (0.53-1.00) | 0.545 (0.42-0.72) |
| Chronos-2 + temperature | 3.952 (2.66-5.48) | 2.211 (1.53-3.11) | 1.301 (0.91-1.88) | 0.843 (0.59-1.20) | 0.715 (0.53-0.95) | 0.574 (0.43-0.77) |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | cannot fit | cannot fit | cannot fit | 0.920 (0.69-1.22) | 0.761 (0.55-1.04) | 0.778 (0.54-1.10) |
| LightGBM (fitted on the context only) | cannot fit | cannot fit | 1.223 (1.00-1.52) | 0.793 (0.62-1.03) | 0.656 (0.51-0.84) | 0.624 (0.48-0.80) |
| LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit | 1.223 (1.00-1.52) | 0.798 (0.62-1.04) | 0.661 (0.51-0.85) | 0.663 (0.50-0.86) |
| Seasonal naive | 1.804 (1.42-2.34) | 1.804 (1.42-2.34) | 0.590 (0.44-0.78) | 0.590 (0.44-0.78) | 0.590 (0.44-0.78) | 1.000 (1.00-1.00) |
| t0-beta | 2.076 (1.41-3.01) | 1.373 (1.08-1.80) | 1.440 (1.12-1.89) | 1.024 (0.74-1.40) | 0.774 (0.57-1.05) | 0.541 (0.41-0.71) |
| t0-beta + temperature | 2.842 (1.86-4.03) | 1.719 (1.27-2.35) | 1.808 (1.30-2.53) | 1.712 (1.26-2.41) | 1.180 (0.81-1.70) | 0.745 (0.51-1.04) |
| t0-gamma | 3.704 (2.71-4.98) | 1.924 (1.53-2.45) | 1.692 (1.30-2.24) | 0.719 (0.52-0.97) | 0.616 (0.44-0.85) | 0.456 (0.36-0.59) |
| t0-gamma + temperature | 2.983 (2.29-3.92) | 1.762 (1.41-2.25) | 1.644 (1.29-2.15) | 0.750 (0.53-1.04) | 0.604 (0.43-0.83) | 0.467 (0.36-0.60) |
| Theory model, fitted on the context + temperature | 1.830 (1.54-2.22) | 1.537 (1.29-1.89) | 0.684 (0.53-0.88) | 0.598 (0.45-0.79) | 0.659 (0.49-0.87) | 0.617 (0.49-0.76) |
| Theory model, structure from 2024 + temperature | 0.600 (0.47-0.75) | 0.662 (0.50-0.85) | 0.597 (0.46-0.76) | 0.610 (0.47-0.78) | 0.594 (0.45-0.77) | 0.619 (0.48-0.78) |
| TimesFM 2.5 | 1.618 (1.26-2.09) | 1.178 (0.95-1.50) | 0.765 (0.57-1.04) | 0.651 (0.49-0.85) | 0.560 (0.42-0.75) | 0.487 (0.39-0.60) |
| TimesFM 3 (non-commercial weights) | 5.596 (3.84-7.72) | 2.210 (1.54-3.10) | 1.066 (0.77-1.46) | 0.562 (0.42-0.75) | 0.537 (0.42-0.70) | 0.447 (0.36-0.57) |
| TimesFM 3 (non-commercial weights) + temperature | 5.692 (3.92-7.80) | 2.011 (1.46-2.74) | 1.705 (1.30-2.27) | 0.591 (0.45-0.78) | 0.534 (0.40-0.73) | 0.451 (0.36-0.58) |
| Timestral 209M | 4.404 (3.02-6.03) | 1.749 (1.30-2.37) | 1.516 (1.18-2.00) | 0.556 (0.41-0.75) | 0.554 (0.41-0.74) | 0.444 (0.34-0.58) |
| Timestral 209M + temperature | 3.480 (2.41-4.72) | 2.003 (1.47-2.70) | 1.894 (1.43-2.53) | 0.599 (0.41-0.84) | 0.551 (0.40-0.74) | 0.498 (0.37-0.66) |
| Timestral 5M | 3.896 (2.71-5.29) | 1.604 (1.20-2.16) | 1.431 (1.13-1.86) | 0.707 (0.52-0.95) | 0.635 (0.47-0.84) | 0.522 (0.39-0.69) |
| Timestral 5M + temperature | 3.583 (2.52-4.85) | 1.670 (1.27-2.22) | 1.667 (1.33-2.14) | 0.831 (0.61-1.12) | 0.671 (0.49-0.91) | 0.577 (0.43-0.77) |

Relative MASE against the seasonal naive at the same length:

| Model | 12 half-hours | 24 half-hours | 48 half-hours | 96 half-hours | 144 half-hours | 336 half-hours |
|---|---|---|---|---|---|---|
| Chronos-2 | 1.361 | 0.934 | 2.478 | 1.137 | 1.214 | 0.526 |
| Chronos-2 + temperature | 1.397 | 1.008 | 2.175 | 1.295 | 1.230 | 0.561 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | cannot fit | cannot fit | cannot fit | 1.586 | 1.297 | 0.677 |
| LightGBM (fitted on the context only) | cannot fit | cannot fit | 2.374 | 1.432 | 1.171 | 0.613 |
| LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit | 2.374 | 1.440 | 1.178 | 0.643 |
| Seasonal naive | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| t0-beta | 0.966 | 0.773 | 2.619 | 1.784 | 1.320 | 0.528 |
| t0-beta + temperature | 1.064 | 0.866 | 2.945 | 2.929 | 1.848 | 0.635 |
| t0-gamma | 1.845 | 1.045 | 2.952 | 1.220 | 1.011 | 0.454 |
| t0-gamma + temperature | 1.579 | 0.975 | 2.931 | 1.217 | 0.990 | 0.462 |
| Theory model, fitted on the context + temperature | 1.097 | 0.906 | 1.236 | 1.038 | 1.148 | 0.617 |
| Theory model, structure from 2024 + temperature | 0.332 | 0.354 | 1.099 | 1.140 | 1.087 | 0.637 |
| TimesFM 2.5 | 0.883 | 0.672 | 1.338 | 1.157 | 0.973 | 0.512 |
| TimesFM 3 (non-commercial weights) | 1.912 | 0.998 | 1.803 | 0.985 | 0.939 | 0.452 |
| TimesFM 3 (non-commercial weights) + temperature | 2.124 | 0.965 | 2.950 | 1.039 | 0.919 | 0.454 |
| Timestral 209M | 1.699 | 0.868 | 2.719 | 0.917 | 0.921 | 0.436 |
| Timestral 209M + temperature | 1.548 | 0.959 | 3.220 | 0.957 | 0.924 | 0.480 |
| Timestral 5M | 1.609 | 0.829 | 2.643 | 1.207 | 1.067 | 0.506 |
| Timestral 5M + temperature | 1.565 | 0.861 | 3.055 | 1.412 | 1.101 | 0.553 |

Relative WQL (pooled):

| Model | 12 half-hours | 24 half-hours | 48 half-hours | 96 half-hours | 144 half-hours | 336 half-hours |
|---|---|---|---|---|---|---|
| Chronos-2 | 2.586 | 1.539 | 1.046 | 0.531 | 0.595 | 0.440 |
| Chronos-2 + temperature | 3.579 | 2.012 | 1.235 | 0.674 | 0.574 | 0.453 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | cannot fit | cannot fit | cannot fit | 0.724 | 0.613 | 0.633 |
| LightGBM (fitted on the context only) | cannot fit | cannot fit | 0.932 | 0.661 | 0.557 | 0.533 |
| LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit | 0.932 | 0.662 | 0.560 | 0.562 |
| Seasonal naive | 1.831 | 1.831 | 0.581 | 0.581 | 0.581 | 1.000 |
| t0-beta | 1.674 | 1.085 | 1.088 | 0.770 | 0.594 | 0.435 |
| t0-beta + temperature | 2.274 | 1.452 | 1.851 | 1.306 | 0.912 | 0.567 |
| t0-gamma | 2.596 | 1.483 | 1.299 | 0.573 | 0.506 | 0.361 |
| t0-gamma + temperature | 2.215 | 1.397 | 1.327 | 0.596 | 0.494 | 0.371 |
| Theory model, fitted on the context + temperature | 1.432 | 1.227 | 0.575 | 0.497 | 0.566 | 0.485 |
| Theory model, structure from 2024 + temperature | 0.475 | 0.512 | 0.465 | 0.474 | 0.466 | 0.483 |
| TimesFM 2.5 | 1.301 | 0.909 | 0.610 | 0.512 | 0.446 | 0.374 |
| TimesFM 3 (non-commercial weights) | 5.580 | 1.709 | 0.874 | 0.468 | 0.434 | 0.352 |
| TimesFM 3 (non-commercial weights) + temperature | 5.606 | 1.687 | 1.568 | 0.500 | 0.440 | 0.361 |
| Timestral 209M | 3.111 | 1.407 | 1.156 | 0.452 | 0.451 | 0.369 |
| Timestral 209M + temperature | 3.475 | 1.804 | 1.634 | 0.507 | 0.457 | 0.408 |
| Timestral 5M | 2.828 | 1.240 | 1.113 | 0.564 | 0.508 | 0.416 |
| Timestral 5M + temperature | 3.072 | 1.651 | 2.166 | 0.689 | 0.535 | 0.456 |

10-90% coverage:

| Model | 12 half-hours | 24 half-hours | 48 half-hours | 96 half-hours | 144 half-hours | 336 half-hours |
|---|---|---|---|---|---|---|
| Chronos-2 | 0.92 | 0.72 | 0.88 | 0.67 | 0.66 | 0.74 |
| Chronos-2 + temperature | 0.99 | 0.93 | 0.99 | 0.71 | 0.72 | 0.78 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | cannot fit | cannot fit | cannot fit | 0.56 | 0.58 | 0.73 |
| LightGBM (fitted on the context only) | cannot fit | cannot fit | 0.71 | 0.49 | 0.47 | 0.46 |
| LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit | 0.71 | 0.50 | 0.48 | 0.46 |
| Seasonal naive | n/a | n/a | n/a | n/a | n/a | n/a |
| t0-beta | 0.89 | 0.86 | 0.91 | 0.85 | 0.76 | 0.82 |
| t0-beta + temperature | 0.96 | 0.91 | 0.96 | 0.77 | 0.77 | 0.84 |
| t0-gamma | 0.89 | 0.88 | 0.94 | 0.83 | 0.81 | 0.88 |
| t0-gamma + temperature | 1.00 | 0.96 | 1.00 | 0.89 | 0.86 | 0.90 |
| Theory model, fitted on the context + temperature | 0.43 | 0.63 | 0.45 | 0.44 | 0.44 | 0.57 |
| Theory model, structure from 2024 + temperature | 0.78 | 0.68 | 0.71 | 0.67 | 0.68 | 0.66 |
| TimesFM 2.5 | 0.70 | 0.88 | 0.87 | 0.81 | 0.81 | 0.86 |
| TimesFM 3 (non-commercial weights) | 0.49 | 0.92 | 0.91 | 0.84 | 0.81 | 0.86 |
| TimesFM 3 (non-commercial weights) + temperature | 0.54 | 0.99 | 1.00 | 0.89 | 0.87 | 0.88 |
| Timestral 209M | 0.88 | 0.95 | 0.92 | 0.86 | 0.84 | 0.90 |
| Timestral 209M + temperature | 0.99 | 1.00 | 1.00 | 0.90 | 0.90 | 0.91 |
| Timestral 5M | 0.85 | 0.94 | 0.93 | 0.87 | 0.79 | 0.85 |
| Timestral 5M + temperature | 1.00 | 0.99 | 1.00 | 0.91 | 0.83 | 0.85 |

### Retail floor sweep, the 80 sweep products (342 windows) (N = 342 windows per length)

Mean-MASE ratio (95% CI), baseline = seasonal naive with the longest history:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.786 (0.68-0.89) |
| Chronos-2 | 0.777 (0.67-0.88) | 0.741 (0.64-0.83) | 0.788 (0.68-0.89) | 0.739 (0.64-0.83) |
| LightGBM (trained on 600 other products) | 3.687 (2.51-5.42) | 1.108 (0.91-1.35) | 0.723 (0.62-0.81) | 0.709 (0.61-0.80) |
| Seasonal naive | 0.777 (0.67-0.88) | 0.777 (0.67-0.88) | 0.777 (0.67-0.88) | 0.777 (0.67-0.88) |
| t0-beta | 0.777 (0.67-0.88) | 0.778 (0.67-0.88) | 0.783 (0.67-0.90) | 0.781 (0.67-0.88) |
| t0-gamma | 0.777 (0.67-0.88) | 0.787 (0.68-0.89) | 0.761 (0.65-0.86) | 0.711 (0.62-0.80) |
| TimesFM 2.5 | 0.777 (0.67-0.88) | 0.815 (0.69-0.94) | 0.731 (0.63-0.82) | 0.691 (0.60-0.78) |
| TimesFM 3 (non-commercial weights) | 0.777 (0.67-0.88) | 1.703 (1.35-2.10) | 0.807 (0.69-0.92) | 0.719 (0.62-0.80) |
| Timestral 209M | 0.777 (0.67-0.88) | 0.926 (0.79-1.08) | 0.769 (0.66-0.87) | 0.710 (0.62-0.80) |
| Timestral 5M | 0.777 (0.67-0.88) | 0.932 (0.79-1.09) | 0.765 (0.66-0.87) | 0.703 (0.61-0.79) |

Geometric-mean relative MASE (95% CI), baseline = seasonal naive with the longest history:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.662 (0.55-0.79) |
| Chronos-2 | 0.298 (0.18-0.50) | 0.348 (0.22-0.52) | 0.364 (0.22-0.57) | 0.381 (0.24-0.56) |
| LightGBM (trained on 600 other products) | 2.200 (1.69-2.90) | 0.890 (0.75-1.06) | 0.365 (0.24-0.53) | 0.276 (0.15-0.48) |
| Seasonal naive | 0.622 (0.52-0.74) | 0.622 (0.52-0.74) | 0.622 (0.52-0.74) | 0.622 (0.52-0.74) |
| t0-beta | 0.622 (0.52-0.74) | 0.622 (0.52-0.74) | 0.620 (0.52-0.73) | 0.604 (0.52-0.71) |
| t0-gamma | 0.622 (0.52-0.74) | 0.626 (0.52-0.74) | 0.610 (0.51-0.72) | 0.574 (0.49-0.67) |
| TimesFM 2.5 | 0.622 (0.52-0.74) | 0.642 (0.54-0.76) | 0.556 (0.46-0.66) | 0.523 (0.43-0.62) |
| TimesFM 3 (non-commercial weights) | 0.622 (0.52-0.74) | 0.939 (0.75-1.17) | 0.613 (0.52-0.73) | 0.554 (0.46-0.66) |
| Timestral 209M | 0.622 (0.52-0.74) | 0.698 (0.57-0.84) | 0.614 (0.51-0.73) | 0.558 (0.47-0.65) |
| Timestral 5M | 0.622 (0.52-0.74) | 0.701 (0.58-0.85) | 0.594 (0.50-0.70) | 0.542 (0.45-0.64) |

Relative MASE against the seasonal naive at the same length:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 1.082 |
| Chronos-2 | 1.000 | 0.949 | 1.032 | 0.962 |
| LightGBM (trained on 600 other products) | 3.415 | 1.438 | 0.915 | 0.884 |
| Seasonal naive | 1.000 | 1.000 | 1.000 | 1.000 |
| t0-beta | 1.000 | 1.000 | 1.007 | 0.968 |
| t0-gamma | 1.000 | 1.012 | 0.979 | 0.928 |
| TimesFM 2.5 | 1.000 | 1.026 | 0.941 | 0.881 |
| TimesFM 3 (non-commercial weights) | 1.000 | 1.523 | 1.031 | 0.938 |
| Timestral 209M | 1.000 | 1.129 | 0.985 | 0.935 |
| Timestral 5M | 1.000 | 1.134 | 0.995 | 0.923 |

Relative WQL (pooled):

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 8.240 |
| Chronos-2 | 0.782 | 0.728 | 0.670 | 0.592 |
| LightGBM (trained on 600 other products) | 0.815 | 0.611 | 0.576 | 0.578 |
| Seasonal naive | 0.785 | 0.785 | 0.785 | 0.785 |
| t0-beta | 0.783 | 0.757 | 0.664 | 0.603 |
| t0-gamma | 0.782 | 0.751 | 0.648 | 0.595 |
| TimesFM 2.5 | 0.785 | 0.668 | 0.592 | 0.585 |
| TimesFM 3 (non-commercial weights) | 0.785 | 1.937 | 0.689 | 0.590 |
| Timestral 209M | 0.785 | 0.817 | 0.631 | 0.585 |
| Timestral 5M | 0.785 | 0.842 | 0.624 | 0.594 |

10-90% coverage:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.84 |
| Chronos-2 | 0.40 | 0.81 | 0.88 | 0.87 |
| LightGBM (trained on 600 other products) | 0.73 | 0.81 | 0.80 | 0.78 |
| Seasonal naive | n/a | n/a | n/a | n/a |
| t0-beta | 0.44 | 0.82 | 0.88 | 0.90 |
| t0-gamma | 0.47 | 0.83 | 0.88 | 0.90 |
| TimesFM 2.5 | 0.33 | 0.74 | 0.76 | 0.78 |
| TimesFM 3 (non-commercial weights) | 0.33 | 0.34 | 0.81 | 0.83 |
| Timestral 209M | 0.33 | 0.79 | 0.82 | 0.81 |
| Timestral 5M | 0.33 | 0.80 | 0.81 | 0.83 |

### Retail floor sweep, the 300-product sample (1,332 windows) (N = 1332 windows per length)

Mean-MASE ratio (95% CI), baseline = seasonal naive with the longest history:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.776 (0.72-0.83) |
| Chronos-2 | 0.836 (0.78-0.89) | 0.784 (0.73-0.84) | 0.841 (0.78-0.90) | 0.762 (0.71-0.81) |
| LightGBM (trained on 600 other products) | 2.737 (2.19-3.38) | 1.010 (0.92-1.11) | 0.728 (0.67-0.78) | 0.716 (0.66-0.77) |
| Seasonal naive | 0.836 (0.78-0.89) | 0.836 (0.78-0.89) | 0.836 (0.78-0.89) | 0.836 (0.78-0.89) |
| t0-beta | 0.836 (0.78-0.89) | 0.836 (0.78-0.89) | 0.824 (0.77-0.88) | 0.795 (0.73-0.86) |
| t0-gamma | 0.836 (0.78-0.89) | 0.854 (0.80-0.91) | 0.799 (0.74-0.85) | 0.733 (0.68-0.79) |
| TimesFM 2.5 | 0.836 (0.78-0.89) | 0.811 (0.76-0.87) | 0.741 (0.69-0.79) | 0.707 (0.65-0.76) |
| TimesFM 3 (non-commercial weights) | 0.836 (0.78-0.89) | 2.126 (1.86-2.40) | 0.866 (0.80-0.94) | 0.729 (0.67-0.78) |
| Timestral 209M | 0.836 (0.78-0.89) | 1.060 (0.98-1.15) | 0.803 (0.75-0.86) | 0.747 (0.69-0.80) |
| Timestral 5M | 0.836 (0.78-0.89) | 1.068 (0.98-1.15) | 0.803 (0.75-0.86) | 0.725 (0.67-0.78) |

Geometric-mean relative MASE (95% CI), baseline = seasonal naive with the longest history:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.649 (0.58-0.71) |
| Chronos-2 | 0.258 (0.19-0.35) | 0.304 (0.23-0.39) | 0.317 (0.24-0.42) | 0.356 (0.28-0.44) |
| LightGBM (trained on 600 other products) | 1.625 (1.42-1.86) | 0.825 (0.75-0.90) | 0.334 (0.26-0.41) | 0.282 (0.21-0.38) |
| Seasonal naive | 0.695 (0.64-0.75) | 0.695 (0.64-0.75) | 0.695 (0.64-0.75) | 0.695 (0.64-0.75) |
| t0-beta | 0.695 (0.64-0.75) | 0.697 (0.65-0.75) | 0.675 (0.62-0.73) | 0.623 (0.57-0.67) |
| t0-gamma | 0.695 (0.64-0.75) | 0.703 (0.65-0.76) | 0.664 (0.62-0.71) | 0.602 (0.56-0.65) |
| TimesFM 2.5 | 0.695 (0.64-0.75) | 0.682 (0.63-0.73) | 0.590 (0.54-0.64) | 0.526 (0.47-0.58) |
| TimesFM 3 (non-commercial weights) | 0.695 (0.64-0.75) | 1.186 (1.08-1.30) | 0.660 (0.61-0.71) | 0.529 (0.48-0.58) |
| Timestral 209M | 0.695 (0.64-0.75) | 0.816 (0.75-0.89) | 0.662 (0.61-0.71) | 0.553 (0.50-0.60) |
| Timestral 5M | 0.695 (0.64-0.75) | 0.819 (0.75-0.89) | 0.637 (0.59-0.69) | 0.536 (0.49-0.59) |

Relative MASE against the seasonal naive at the same length:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.993 |
| Chronos-2 | 1.000 | 0.949 | 1.007 | 0.919 |
| LightGBM (trained on 600 other products) | 2.222 | 1.210 | 0.880 | 0.853 |
| Seasonal naive | 1.000 | 1.000 | 1.000 | 1.000 |
| t0-beta | 1.000 | 1.003 | 0.992 | 0.912 |
| t0-gamma | 1.000 | 1.019 | 0.970 | 0.884 |
| TimesFM 2.5 | 1.000 | 0.992 | 0.912 | 0.852 |
| TimesFM 3 (non-commercial weights) | 1.000 | 1.716 | 1.020 | 0.899 |
| Timestral 209M | 1.000 | 1.177 | 0.972 | 0.901 |
| Timestral 5M | 1.000 | 1.183 | 0.981 | 0.890 |

Relative WQL (pooled):

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 6.050 |
| Chronos-2 | 0.762 | 0.699 | 0.655 | 0.566 |
| LightGBM (trained on 600 other products) | 0.725 | 0.577 | 0.545 | 0.543 |
| Seasonal naive | 0.766 | 0.766 | 0.766 | 0.766 |
| t0-beta | 0.763 | 0.726 | 0.654 | 0.571 |
| t0-gamma | 0.761 | 0.725 | 0.628 | 0.558 |
| TimesFM 2.5 | 0.766 | 0.609 | 0.558 | 0.536 |
| TimesFM 3 (non-commercial weights) | 0.766 | 2.276 | 0.673 | 0.546 |
| Timestral 209M | 0.766 | 0.841 | 0.599 | 0.545 |
| Timestral 5M | 0.766 | 0.876 | 0.597 | 0.543 |

10-90% coverage:

| Model | 1 weeks | 2 weeks | 4 weeks | 8 weeks |
|---|---|---|---|---|
| AutoETS (spreadsheet stand-in) | cannot fit | cannot fit | cannot fit | 0.84 |
| Chronos-2 | 0.33 | 0.82 | 0.88 | 0.87 |
| LightGBM (trained on 600 other products) | 0.76 | 0.80 | 0.78 | 0.77 |
| Seasonal naive | n/a | n/a | n/a | n/a |
| t0-beta | 0.35 | 0.83 | 0.88 | 0.89 |
| t0-gamma | 0.38 | 0.83 | 0.88 | 0.89 |
| TimesFM 2.5 | 0.27 | 0.72 | 0.76 | 0.78 |
| TimesFM 3 (non-commercial weights) | 0.27 | 0.28 | 0.80 | 0.83 |
| Timestral 209M | 0.27 | 0.79 | 0.81 | 0.81 |
| Timestral 5M | 0.27 | 0.80 | 0.81 | 0.83 |

### Head to head on the same windows (below 1 = first model better; 95% CIs resample whole series)

| Task | Model | Against | Ratio of mean MASE (95% CI) | Geometric mean of MASE ratios (95% CI) |
|---|---|---|---|---|
| retail | Timestral 209M | LightGBM (global, fitted) | 0.967 (0.95-0.99) | 0.802 (0.75-0.85) |
| retail | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.861 (0.82-0.90) | 0.568 (0.51-0.63) |
| retail | Timestral 209M | Chronos-2 | 1.001 (0.98-1.02) | 0.910 (0.87-0.94) |
| retail | Timestral 209M | Seasonal naive | 0.696 (0.64-0.75) | 0.464 (0.42-0.52) |
| retail_calendar | Timestral 209M + calendar covariates | Timestral 209M | 1.012 (1.00-1.03) | 0.990 (0.96-1.02) |
| retail_calendar | Timestral 209M + calendar covariates | LightGBM (global, fitted) | 0.978 (0.95-1.01) | 0.820 (0.77-0.87) |
| retail_calendar | Timestral 209M + calendar covariates | AutoETS (spreadsheet stand-in) | 0.871 (0.83-0.91) | 0.593 (0.54-0.65) |
| retail_calendar | Timestral 209M + calendar covariates | Chronos-2 | 1.012 (0.99-1.05) | 0.926 (0.89-0.97) |
| retail_calendar | Timestral 209M + calendar covariates | Seasonal naive | 0.704 (0.65-0.76) | 0.487 (0.44-0.54) |
| fresh | Timestral 209M | LightGBM (global, fitted) | 0.955 (0.93-0.98) | 0.966 (0.94-0.99) |
| fresh | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.962 (0.94-0.98) | 0.946 (0.93-0.97) |
| fresh | Timestral 209M | Chronos-2 | 0.984 (0.97-0.99) | 0.992 (0.98-1.00) |
| fresh | Timestral 209M | Seasonal naive | 0.823 (0.80-0.85) | 0.805 (0.78-0.83) |
| fresh_promo | Timestral 209M + discount, holiday, activity | LightGBM (global, fitted) + discount, holiday, activity | 0.958 (0.92-0.99) | 0.974 (0.94-1.00) |
| fresh_promo | Timestral 209M + discount, holiday, activity | Timestral 209M | 0.987 (0.96-1.01) | 0.985 (0.96-1.01) |
| retail_sweep_L08 | Timestral 209M | LightGBM (global, fitted) | 0.845 (0.79-0.89) | 0.789 (0.71-0.88) |
| retail_sweep_L08 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.904 (0.85-0.96) | 0.782 (0.69-0.88) |
| retail_sweep_L08 | Timestral 209M | Chronos-2 | 0.961 (0.91-0.99) | 0.930 (0.88-0.97) |
| retail_sweep_L08 | Timestral 209M | Seasonal naive | 0.914 (0.85-0.97) | 0.935 (0.89-0.99) |
| retail_sweep_L13 | Timestral 209M | LightGBM (global, fitted) | 0.914 (0.87-0.96) | 0.798 (0.71-0.88) |
| retail_sweep_L13 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.853 (0.80-0.90) | 0.699 (0.58-0.83) |
| retail_sweep_L13 | Timestral 209M | Chronos-2 | 0.981 (0.96-1.01) | 0.880 (0.81-0.95) |
| retail_sweep_L13 | Timestral 209M | Seasonal naive | 0.893 (0.82-0.95) | 0.885 (0.84-0.94) |
| retail_sweep_L26 | Timestral 209M | LightGBM (global, fitted) | 0.896 (0.87-0.93) | 0.769 (0.69-0.84) |
| retail_sweep_L26 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.789 (0.67-0.90) | 0.633 (0.49-0.83) |
| retail_sweep_L26 | Timestral 209M | Chronos-2 | 0.981 (0.95-1.00) | 0.888 (0.82-0.95) |
| retail_sweep_L26 | Timestral 209M | Seasonal naive | 0.868 (0.79-0.94) | 0.854 (0.81-0.91) |
| retail_sweep_L52 | Timestral 209M | LightGBM (global, fitted) | 0.947 (0.91-0.98) | 0.749 (0.65-0.84) |
| retail_sweep_L52 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.857 (0.79-0.92) | 0.595 (0.46-0.78) |
| retail_sweep_L52 | Timestral 209M | Chronos-2 | 0.986 (0.95-1.02) | 0.876 (0.79-0.95) |
| retail_sweep_L52 | Timestral 209M | Seasonal naive | 0.672 (0.58-0.75) | 0.446 (0.36-0.55) |
| retail_sweep_L78 | Timestral 209M | LightGBM (global, fitted) | 0.915 (0.88-0.95) | 0.712 (0.63-0.79) |
| retail_sweep_L78 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.824 (0.74-0.89) | 0.572 (0.47-0.68) |
| retail_sweep_L78 | Timestral 209M | Chronos-2 | 0.989 (0.96-1.02) | 0.917 (0.87-0.96) |
| retail_sweep_L78 | Timestral 209M | Seasonal naive | 0.676 (0.59-0.76) | 0.457 (0.37-0.56) |
| retail_floor_L01 | Timestral 209M | Seasonal naive | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail_floor_L01 | Timestral 209M | LightGBM (trained on 600 other products) | 0.211 (0.15-0.30) | 0.293 (0.22-0.38) |
| retail_floor_L01 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L01 | Timestral 209M | Chronos-2 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail_floor_L01 | Timestral 5M | Seasonal naive | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail_floor_L01 | Timestral 5M | LightGBM (trained on 600 other products) | 0.211 (0.15-0.30) | 0.293 (0.22-0.38) |
| retail_floor_L01 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L01 | Timestral 5M | Chronos-2 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail_floor_L02 | Timestral 209M | Seasonal naive | 1.192 (1.13-1.28) | 1.129 (1.09-1.17) |
| retail_floor_L02 | Timestral 209M | LightGBM (trained on 600 other products) | 0.836 (0.71-0.97) | 0.785 (0.68-0.89) |
| retail_floor_L02 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L02 | Timestral 209M | Chronos-2 | 1.250 (1.17-1.36) | 1.188 (1.14-1.25) |
| retail_floor_L02 | Timestral 5M | Seasonal naive | 1.199 (1.13-1.29) | 1.134 (1.09-1.18) |
| retail_floor_L02 | Timestral 5M | LightGBM (trained on 600 other products) | 0.841 (0.72-0.97) | 0.788 (0.69-0.90) |
| retail_floor_L02 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L02 | Timestral 5M | Chronos-2 | 1.258 (1.17-1.37) | 1.193 (1.14-1.25) |
| retail_floor_L04 | Timestral 209M | Seasonal naive | 0.990 (0.95-1.03) | 0.985 (0.95-1.02) |
| retail_floor_L04 | Timestral 209M | LightGBM (trained on 600 other products) | 1.064 (1.00-1.15) | 1.074 (1.02-1.13) |
| retail_floor_L04 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L04 | Timestral 209M | Chronos-2 | 0.976 (0.94-1.01) | 0.954 (0.92-0.99) |
| retail_floor_L04 | Timestral 5M | Seasonal naive | 0.984 (0.94-1.03) | 0.995 (0.96-1.03) |
| retail_floor_L04 | Timestral 5M | LightGBM (trained on 600 other products) | 1.058 (1.00-1.15) | 1.052 (0.99-1.11) |
| retail_floor_L04 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail_floor_L04 | Timestral 5M | Chronos-2 | 0.971 (0.94-1.00) | 0.942 (0.91-0.97) |
| retail_floor_L08 | Timestral 209M | Seasonal naive | 0.914 (0.85-0.97) | 0.935 (0.89-0.99) |
| retail_floor_L08 | Timestral 209M | LightGBM (trained on 600 other products) | 1.002 (0.96-1.06) | 1.534 (1.14-2.27) |
| retail_floor_L08 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.904 (0.85-0.96) | 0.782 (0.69-0.88) |
| retail_floor_L08 | Timestral 209M | Chronos-2 | 0.961 (0.91-0.99) | 0.930 (0.88-0.97) |
| retail_floor_L08 | Timestral 5M | Seasonal naive | 0.905 (0.83-0.97) | 0.923 (0.87-0.98) |
| retail_floor_L08 | Timestral 5M | LightGBM (trained on 600 other products) | 0.992 (0.96-1.03) | 1.533 (1.14-2.22) |
| retail_floor_L08 | Timestral 5M | AutoETS (spreadsheet stand-in) | 0.894 (0.84-0.94) | 0.732 (0.62-0.84) |
| retail_floor_L08 | Timestral 5M | Chronos-2 | 0.951 (0.89-0.99) | 0.898 (0.84-0.95) |
| retail300_floor_L01 | Timestral 209M | Seasonal naive | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail300_floor_L01 | Timestral 209M | LightGBM (trained on 600 other products) | 0.305 (0.25-0.38) | 0.450 (0.39-0.51) |
| retail300_floor_L01 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L01 | Timestral 209M | Chronos-2 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail300_floor_L01 | Timestral 5M | Seasonal naive | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail300_floor_L01 | Timestral 5M | LightGBM (trained on 600 other products) | 0.305 (0.25-0.38) | 0.450 (0.39-0.51) |
| retail300_floor_L01 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L01 | Timestral 5M | Chronos-2 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) |
| retail300_floor_L02 | Timestral 209M | Seasonal naive | 1.269 (1.22-1.32) | 1.177 (1.15-1.20) |
| retail300_floor_L02 | Timestral 209M | LightGBM (trained on 600 other products) | 1.050 (0.95-1.15) | 0.973 (0.91-1.03) |
| retail300_floor_L02 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L02 | Timestral 209M | Chronos-2 | 1.352 (1.28-1.43) | 1.241 (1.21-1.27) |
| retail300_floor_L02 | Timestral 5M | Seasonal naive | 1.278 (1.22-1.33) | 1.183 (1.16-1.21) |
| retail300_floor_L02 | Timestral 5M | LightGBM (trained on 600 other products) | 1.057 (0.96-1.16) | 0.977 (0.92-1.04) |
| retail300_floor_L02 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L02 | Timestral 5M | Chronos-2 | 1.362 (1.28-1.44) | 1.246 (1.22-1.28) |
| retail300_floor_L04 | Timestral 209M | Seasonal naive | 0.961 (0.94-0.99) | 0.972 (0.96-0.99) |
| retail300_floor_L04 | Timestral 209M | LightGBM (trained on 600 other products) | 1.103 (1.07-1.14) | 1.099 (1.07-1.13) |
| retail300_floor_L04 | Timestral 209M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L04 | Timestral 209M | Chronos-2 | 0.955 (0.93-0.98) | 0.960 (0.94-0.98) |
| retail300_floor_L04 | Timestral 5M | Seasonal naive | 0.961 (0.94-0.98) | 0.981 (0.97-1.00) |
| retail300_floor_L04 | Timestral 5M | LightGBM (trained on 600 other products) | 1.102 (1.06-1.14) | 1.084 (1.05-1.11) |
| retail300_floor_L04 | Timestral 5M | AutoETS (spreadsheet stand-in) | cannot fit | cannot fit |
| retail300_floor_L04 | Timestral 5M | Chronos-2 | 0.955 (0.94-0.97) | 0.946 (0.93-0.96) |
| retail300_floor_L08 | Timestral 209M | Seasonal naive | 0.894 (0.86-0.93) | 0.901 (0.88-0.93) |
| retail300_floor_L08 | Timestral 209M | LightGBM (trained on 600 other products) | 1.042 (1.01-1.07) | 1.325 (1.15-1.56) |
| retail300_floor_L08 | Timestral 209M | AutoETS (spreadsheet stand-in) | 0.962 (0.93-1.00) | 0.798 (0.74-0.86) |
| retail300_floor_L08 | Timestral 209M | Chronos-2 | 0.980 (0.96-1.00) | 0.923 (0.89-0.95) |
| retail300_floor_L08 | Timestral 5M | Seasonal naive | 0.867 (0.83-0.91) | 0.890 (0.86-0.92) |
| retail300_floor_L08 | Timestral 5M | LightGBM (trained on 600 other products) | 1.012 (0.99-1.03) | 1.425 (1.20-1.75) |
| retail300_floor_L08 | Timestral 5M | AutoETS (spreadsheet stand-in) | 0.933 (0.90-0.96) | 0.755 (0.69-0.83) |
| retail300_floor_L08 | Timestral 5M | Chronos-2 | 0.951 (0.93-0.98) | 0.901 (0.87-0.93) |
| grid_floor_L0012 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit |
| grid_floor_L0012 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 5.802 (3.78-8.46) | 4.659 (3.24-6.90) |
| grid_floor_L0012 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 1.902 (1.35-2.51) | 1.411 (1.07-1.87) |
| grid_floor_L0012 | Timestral 209M | Seasonal naive | 2.441 (1.89-2.95) | 1.699 (1.30-2.22) |
| grid_floor_L0012 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit |
| grid_floor_L0012 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 5.973 (3.93-8.66) | 4.710 (3.16-7.13) |
| grid_floor_L0012 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 1.958 (1.41-2.54) | 1.427 (1.06-1.91) |
| grid_floor_L0012 | Timestral 5M | Seasonal naive | 2.160 (1.67-2.69) | 1.609 (1.27-2.03) |
| grid_floor_L0024 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit |
| grid_floor_L0024 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 3.025 (2.00-4.42) | 2.706 (1.75-4.25) |
| grid_floor_L0024 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 1.303 (1.04-1.56) | 1.058 (0.88-1.28) |
| grid_floor_L0024 | Timestral 209M | Seasonal naive | 0.970 (0.83-1.12) | 0.868 (0.77-0.99) |
| grid_floor_L0024 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | cannot fit | cannot fit |
| grid_floor_L0024 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 2.523 (1.76-3.58) | 2.429 (1.68-3.60) |
| grid_floor_L0024 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 1.087 (0.91-1.27) | 0.950 (0.83-1.09) |
| grid_floor_L0024 | Timestral 5M | Seasonal naive | 0.889 (0.77-1.05) | 0.829 (0.76-0.94) |
| grid_floor_L0048 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | 1.549 (1.29-1.81) | 1.356 (1.16-1.60) |
| grid_floor_L0048 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 3.172 (2.31-4.33) | 2.931 (2.13-4.13) |
| grid_floor_L0048 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 2.769 (2.13-3.52) | 2.606 (2.08-3.25) |
| grid_floor_L0048 | Timestral 209M | Seasonal naive | 2.568 (2.00-3.35) | 2.719 (2.14-3.47) |
| grid_floor_L0048 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | 1.363 (1.21-1.53) | 1.287 (1.13-1.46) |
| grid_floor_L0048 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 2.792 (2.19-3.59) | 2.780 (2.12-3.67) |
| grid_floor_L0048 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 2.437 (2.00-2.97) | 2.472 (2.06-2.94) |
| grid_floor_L0048 | Timestral 5M | Seasonal naive | 2.424 (1.95-3.07) | 2.643 (2.13-3.32) |
| grid_floor_L0096 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | 0.750 (0.63-0.88) | 0.665 (0.57-0.77) |
| grid_floor_L0096 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 0.981 (0.75-1.24) | 0.840 (0.68-1.05) |
| grid_floor_L0096 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 1.002 (0.84-1.20) | 0.922 (0.83-1.04) |
| grid_floor_L0096 | Timestral 209M | Seasonal naive | 0.941 (0.86-1.04) | 0.917 (0.85-0.99) |
| grid_floor_L0096 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | 1.041 (0.90-1.22) | 0.980 (0.85-1.14) |
| grid_floor_L0096 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 1.361 (1.11-1.66) | 1.239 (1.03-1.49) |
| grid_floor_L0096 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 1.390 (1.16-1.69) | 1.360 (1.18-1.60) |
| grid_floor_L0096 | Timestral 5M | Seasonal naive | 1.197 (1.06-1.39) | 1.207 (1.07-1.37) |
| grid_floor_L0144 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | 0.834 (0.72-0.96) | 0.784 (0.70-0.88) |
| grid_floor_L0144 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 0.928 (0.73-1.15) | 0.850 (0.69-1.04) |
| grid_floor_L0144 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 0.837 (0.71-0.97) | 0.804 (0.69-0.92) |
| grid_floor_L0144 | Timestral 209M | Seasonal naive | 0.939 (0.81-1.09) | 0.921 (0.81-1.03) |
| grid_floor_L0144 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | 1.015 (0.88-1.18) | 0.934 (0.84-1.05) |
| grid_floor_L0144 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 1.129 (0.88-1.41) | 1.013 (0.80-1.27) |
| grid_floor_L0144 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 1.018 (0.85-1.19) | 0.959 (0.82-1.11) |
| grid_floor_L0144 | Timestral 5M | Seasonal naive | 1.076 (0.96-1.23) | 1.067 (0.97-1.17) |
| grid_floor_L0336 | Timestral 209M + temperature | LightGBM (fitted on the context only) + temperature | 0.752 (0.64-0.88) | 0.746 (0.64-0.87) |
| grid_floor_L0336 | Timestral 209M + temperature | Theory model, structure from 2024 + temperature | 0.805 (0.62-1.02) | 0.754 (0.60-0.94) |
| grid_floor_L0336 | Timestral 209M + temperature | Theory model, fitted on the context + temperature | 0.808 (0.63-1.01) | 0.778 (0.63-0.95) |
| grid_floor_L0336 | Timestral 209M | Seasonal naive | 0.444 (0.34-0.58) | 0.436 (0.33-0.56) |
| grid_floor_L0336 | Timestral 5M + temperature | LightGBM (fitted on the context only) + temperature | 0.871 (0.72-1.07) | 0.860 (0.71-1.05) |
| grid_floor_L0336 | Timestral 5M + temperature | Theory model, structure from 2024 + temperature | 0.932 (0.72-1.19) | 0.868 (0.68-1.10) |
| grid_floor_L0336 | Timestral 5M + temperature | Theory model, fitted on the context + temperature | 0.935 (0.75-1.14) | 0.897 (0.74-1.08) |
| grid_floor_L0336 | Timestral 5M | Seasonal naive | 0.522 (0.39-0.69) | 0.506 (0.37-0.68) |

### Out of range: summer context (1 Jun-31 Aug 2025), one forecast to 30 Nov, scored on 1 Oct-30 Nov (2,930 half-hours)

| Model | Windows | Series | Geo. rel. MASE (95% CI) | Mean-MASE ratio (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|---|
| Theory model, structure from 2024 + temperature | 1 | 1 | 0.283 (n/a-n/a) | 0.283 (n/a-n/a) | 0.232 | 1.159 | 0.057 | 0.46 | 0.0065 |
| Theory model, fitted on the context + temperature | 1 | 1 | 0.894 (n/a-n/a) | 0.894 (n/a-n/a) | 0.812 | 3.656 | 0.198 | 0.21 | 0.0040 |
| LightGBM (calendar, no lags) + temperature | 1 | 1 | 0.899 (n/a-n/a) | 0.899 (n/a-n/a) | 0.847 | 3.676 | 0.206 | 0.09 | 61.0020 |
| Chronos-2 + temperature | 1 | 1 | 0.905 (n/a-n/a) | 0.905 (n/a-n/a) | 0.777 | 3.704 | 0.189 | 0.23 | 13.9092 |
| Chronos-2 | 1 | 1 | 0.911 (n/a-n/a) | 0.911 (n/a-n/a) | 0.785 | 3.727 | 0.191 | 0.26 | 8.0649 |
| Timestral 209M | 1 | 1 | 0.915 (n/a-n/a) | 0.915 (n/a-n/a) | 0.889 | 3.745 | 0.216 | 0.02 | 2.0288 |
| t0-beta | 1 | 1 | 0.918 (n/a-n/a) | 0.918 (n/a-n/a) | 0.850 | 3.754 | 0.207 | 0.14 | 11.6246 |
| Timestral 209M + temperature | 1 | 1 | 0.963 (n/a-n/a) | 0.963 (n/a-n/a) | 0.937 | 3.941 | 0.228 | 0.02 | 6.6550 |
| t0-beta + temperature | 1 | 1 | 0.972 (n/a-n/a) | 0.972 (n/a-n/a) | 0.850 | 3.977 | 0.207 | 0.36 | 21.9700 |
| Timestral 5M | 1 | 1 | 0.988 (n/a-n/a) | 0.988 (n/a-n/a) | 0.945 | 4.042 | 0.230 | 0.09 | 0.1755 |
| Seasonal naive | 1 | 1 | 1.000 (n/a-n/a) | 1.000 (n/a-n/a) | 1.000 | 4.091 | 0.243 | n/a | 0.0007 |
| Timestral 5M + temperature | 1 | 1 | 1.039 (n/a-n/a) | 1.039 (n/a-n/a) | 0.996 | 4.251 | 0.242 | 0.07 | 0.4121 |
| t0-gamma + temperature | 1 | 1 | 1.041 (n/a-n/a) | 1.041 (n/a-n/a) | 0.928 | 4.258 | 0.226 | 0.14 | 26.3512 |
| TimesFM 3 (non-commercial weights) | 1 | 1 | 1.058 (n/a-n/a) | 1.058 (n/a-n/a) | 0.905 | 4.327 | 0.220 | 0.16 | 0.8802 |
| t0-gamma | 1 | 1 | 1.068 (n/a-n/a) | 1.068 (n/a-n/a) | 0.962 | 4.371 | 0.234 | 0.10 | 13.4544 |
| LightGBM (calendar, no lags) | 1 | 1 | 1.091 (n/a-n/a) | 1.091 (n/a-n/a) | 1.005 | 4.462 | 0.245 | 0.05 | 55.8843 |
| TimesFM 3 (non-commercial weights) + temperature | 1 | 1 | 1.128 (n/a-n/a) | 1.128 (n/a-n/a) | 0.970 | 4.613 | 0.236 | 0.13 | 1.6115 |
| TimesFM 2.5 | 1 | 1 | 1.156 (n/a-n/a) | 1.156 (n/a-n/a) | 1.137 | 4.729 | 0.277 | 0.02 | 4.8652 |
| AutoETS (spreadsheet stand-in) | 1 | 1 | 1.397 (n/a-n/a) | 1.397 (n/a-n/a) | 1.516 | 5.715 | 0.369 | 1.00 | 4.3917 |
| ETS(A,A,A) (Excel FORECAST.ETS structure) | 1 | 1 | 1.456 (n/a-n/a) | 1.456 (n/a-n/a) | 1.257 | 5.956 | 0.306 | 0.07 | 1.1274 |

### Out of range, day ahead: the same summer context frozen, a gap of missing values to each forecast day, 61 day-ahead forecasts for 1 Oct-30 Nov

| Model | Windows | Series | Geo. rel. MASE (95% CI) | Mean-MASE ratio (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |
|---|---|---|---|---|---|---|---|---|---|
| Theory model, structure from 2024 + temperature | 61 | 1 | 0.290 (0.26-0.32) | 0.283 (0.26-0.31) | 0.232 | 1.159 | 0.056 | 0.46 | 0.0046 |
| Theory model, fitted on the context + temperature | 61 | 1 | 0.901 (0.84-0.95) | 0.894 (0.84-0.94) | 0.812 | 3.658 | 0.198 | 0.21 | 0.0027 |
| Timestral 5M | 61 | 1 | 0.957 (0.90-1.02) | 0.950 (0.90-1.00) | 0.773 | 3.888 | 0.188 | 0.45 | 0.0161 |
| Timestral 209M | 61 | 1 | 0.974 (0.92-1.02) | 0.967 (0.92-1.01) | 0.804 | 3.957 | 0.196 | 0.38 | 0.3695 |
| Seasonal naive | 61 | 1 | 1.000 (1.00-1.00) | 1.000 (1.00-1.00) | 1.000 | 4.094 | 0.243 | n/a | 0.0001 |
| Chronos-2 | 61 | 1 | 1.003 (0.93-1.08) | 1.002 (0.93-1.07) | 0.847 | 4.101 | 0.206 | 0.47 | 0.2189 |
| Timestral 5M + temperature | 61 | 1 | 1.018 (0.95-1.08) | 1.012 (0.95-1.07) | 0.814 | 4.144 | 0.198 | 0.46 | 0.0643 |
| Timestral 209M + temperature | 61 | 1 | 1.033 (0.98-1.08) | 1.025 (0.98-1.08) | 0.835 | 4.197 | 0.203 | 0.43 | 1.4504 |
| Chronos-2 + temperature | 61 | 1 | 1.068 (1.00-1.14) | 1.076 (1.01-1.14) | 0.846 | 4.405 | 0.206 | 0.71 | 0.3907 |
| t0-beta | 61 | 1 | 1.193 (1.12-1.27) | 1.156 (1.09-1.22) | 1.097 | 4.731 | 0.267 | 0.07 | 0.4260 |
| t0-gamma + temperature | 61 | 1 | 1.223 (1.16-1.29) | 1.179 (1.12-1.24) | 1.114 | 4.828 | 0.271 | 0.05 | 1.0270 |
| t0-gamma | 61 | 1 | 1.229 (1.16-1.30) | 1.180 (1.12-1.24) | 1.119 | 4.829 | 0.272 | 0.04 | 0.5001 |
| t0-beta + temperature | 61 | 1 | 1.230 (1.15-1.31) | 1.196 (1.13-1.27) | 1.130 | 4.896 | 0.275 | 0.07 | 0.8506 |
