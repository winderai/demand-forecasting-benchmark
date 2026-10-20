"""Stage 5: charts (charts/*.svg, *.png) and results/demo.json from results/summary.json and the forecasts."""

import argparse
import json
from pathlib import Path

import pandas as pd

from forecastbench import report

RETAIL_SWEEP = [8, 13, 26, 52, 78]
GRID_SWEEP = [48, 336, 1344, 4032]
DEMO_CUTOFFS = ["2011-06-19", "2011-07-17", "2011-08-14", "2011-09-11", "2011-10-09"]
DEMO_GRID_WEEK = ["2025-07-06", "2025-07-07", "2025-07-08", "2025-07-09", "2025-07-10", "2025-07-11", "2025-07-12"]
EXAMPLE_MODELS = ["autoets", "lightgbm", "timestral-209m"]
GRID_FLOOR = [12, 24, 48, 96, 144, 336]
RETAIL_FLOOR = [1, 2, 4, 8]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecasts", type=Path, default=Path("results/forecasts"))
    parser.add_argument("--summary", type=Path, default=Path("results/summary.json"))
    parser.add_argument("--charts", type=Path, default=Path("charts"))
    parser.add_argument("--demo", type=Path, default=Path("results/demo.json"))
    args = parser.parse_args()
    summary = report.Summary(args.summary)
    products = pd.read_parquet("data/prepared/retail_products.parquet")
    report.bars(summary, args.charts)
    retail = report.sweep_curves(summary, "retail_sweep_L", RETAIL_SWEEP)
    report.sweep_chart(retail, RETAIL_SWEEP, "weeks",
                       f"Retail: {retail['n_series']} products with 78+ weeks of history, {retail['n_windows']} windows",
                       args.charts / "sweep_retail", [str(n) for n in RETAIL_SWEEP],
                       "Lower is better. Same targets at every length; 1 = seasonal naive with the full history. Below 52 "
                       "weeks seasonal naive has no year-ago week and repeats the last week. Dashed: fitted models.")
    grid = report.sweep_curves(summary, "grid_sweep_L", GRID_SWEEP)
    report.sweep_chart(grid, GRID_SWEEP, "half-hours", f"GB demand 2025: {grid['n_windows']} day-ahead forecasts",
                       args.charts / "sweep_grid", ["1 day", "1 week", "4 weeks", "12 weeks"],
                       "Lower is better. Same targets at every length; 1 = seasonal naive (same half-hour last week) with 12 "
                       "weeks. No temperature for any model. Dashed: fitted models (LightGBM fitted on the context alone).")
    picks = report.pick_products(args.forecasts, products, DEMO_CUTOFFS)
    best = next(p for p in picks if p["role"] == "best-seller")
    report.example_chart(args.forecasts, products, args.charts, best["code"], best["cutoffs"][-1], EXAMPLE_MODELS)
    report.demo(args.forecasts, summary, products, picks, DEMO_GRID_WEEK, retail, RETAIL_SWEEP, args.demo)
    grid_floor = report.floor_curves(summary, [(n, f"grid_floor_L{n:04d}") for n in GRID_FLOOR], report.FLOOR_GRID_MODELS)
    report.floor_chart(grid_floor, GRID_FLOOR, ["6 h", "12 h", "1 day", "2 days", "3 days", "7 days"], "half-hours",
                       "GB demand: 28 day-ahead forecasts across 2025", "Lower is better. 1 = seasonal naive (same "
                       "half-hour last week) with 7 days. Every model that takes temperature gets it (measured, an oracle). "
                       "Band: Timestral 209M's 95% interval. Missing points: cannot fit.\nSeasonal naive: last value under 1 day, "
                       "same half-hour yesterday for 1-3 days, same half-hour last week at 7 days.",
                       args.charts / "floor_grid", "timestral-209m+temperature")
    retail_floor = report.floor_curves(
        summary, [(n, f"retail_floor_L{n:02d}") for n in RETAIL_FLOOR] + [(n, f"retail_sweep_L{n:02d}") for n in RETAIL_SWEEP],
        [(m, "") for m in ["seasonal-naive", "autoets", "lightgbm-transfer", "lightgbm", "timestral-5m",
                           "timestral-209m", "chronos-2", "timesfm-3", "t0-gamma"]])
    lengths = RETAIL_FLOOR + RETAIL_SWEEP[1:]
    report.floor_chart(retail_floor, lengths, [str(n) for n in lengths], "weeks",
                       "Retail: 80 products, 342 windows, 1 to 78 weeks of history",
                       "Lower is better. Left: mean MASE over seasonal naive's mean MASE with the full history (the geometric "
                       "mean is distorted by exact-zero errors on intermittent products).\nLightGBM trained on 600 other products "
                       "at 1-8 weeks; LightGBM fitted on the products' own truncated histories at 8-78 weeks.",
                       args.charts / "floor_retail", "timestral-209m", "relative_mase_of_means",
                       "Mean MASE relative to seasonal naive")
    report.extrapolation_chart(args.forecasts, args.charts / "extrapolation")
    report.extend_demo(args.demo, summary, args.forecasts, GRID_FLOOR, RETAIL_FLOOR)
    (args.charts / "demo_picks.json").write_text(json.dumps(picks, indent=2))
    print(f"charts in {args.charts}, demo in {args.demo} ({args.demo.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
