"""Stage 3: run every contender over every backtest task and keep the forecasts in results/forecasts/.

Every default lives here. A finished (task, model) pair is cached; --force reruns it.
"""

import argparse
import json
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
warnings.filterwarnings("ignore")

from forecastbench import contenders as C  # noqa: E402
from forecastbench.backtest import Run  # noqa: E402
from forecastbench.fresh import FreshRetail  # noqa: E402
from forecastbench.windows import GridBacktest, RetailBacktest  # noqa: E402

THREADS = 8
LIGHTGBM_THREADS = 1  # faster than 8 on this shared machine: 1.9 s vs 4.9 s per 25k-row fit
SEED = 2026

RETAIL_HORIZON = 8
RETAIL_CUTOFFS = ["2011-06-19", "2011-07-17", "2011-08-14", "2011-09-11", "2011-10-09"]
RETAIL_MIN_HISTORY = 8
RETAIL_LIVE_WEEKS = 13
RETAIL_PRODUCTS = 300
RETAIL_SWEEP = [8, 13, 26, 52, 78]
RETAIL_SWEEP_PRODUCTS = 80

GRID_HORIZON = 48
GRID_CONTEXT = 4096
GRID_TRAINING_DAYS = 365
GRID_HISTORIC_BLOCKS = [("2025-01-13", 7), ("2025-04-28", 7), ("2025-07-07", 7), ("2025-10-06", 7)]
GRID_SWEEP_DAYS = [0, 3, 5]  # Monday, Thursday, Saturday of each block
GRID_LEAK_FREE_DAYS = ("2026-10-15", 5)
GRID_SWEEP = [48, 336, 1344, 4032]

FRESH_SERIES = 400

REPOS = {
    "timestral-5m": "mistralai/Timestral-5M",
    "timestral-209m": "mistralai/Timestral-209M",
    "chronos-2": "amazon/chronos-2",
    "timesfm-2.5": "google/timesfm-2.5-200m-pytorch",
    "timesfm-3": "google/timesfm-3.0-pytorch",
    "t0-gamma": "theforecastingcompany/t0-gamma",
    "t0-beta": "theforecastingcompany/t0-beta",
}


def midnights(start: str, days: int) -> list[pd.Timestamp]:
    local = pd.date_range(start, periods=days, freq="D", tz="Europe/London")
    return [d.tz_convert("UTC") for d in local]


def retail_tasks(prepared: Path, sample: int, sweep_sample: int):
    frame = pd.read_parquet(prepared / "retail_weekly.parquet")
    backtest = RetailBacktest(frame, RETAIL_HORIZON, RETAIL_MIN_HISTORY, RETAIL_LIVE_WEEKS)
    pairs = backtest.eligible([pd.Timestamp(c) for c in RETAIL_CUTOFFS])
    rng = np.random.default_rng(SEED)
    codes = np.sort(pairs["unique_id"].unique())
    chosen = set(rng.choice(codes, size=sample, replace=False))
    main = pairs[pairs["unique_id"].isin(chosen)].sort_values(["cutoff", "unique_id"]).reset_index(drop=True)
    long = main[main["history"] >= max(RETAIL_SWEEP)]
    long_products = np.sort(long["unique_id"].unique())
    sweep_codes = set(rng.choice(long_products, size=min(sweep_sample, len(long_products)), replace=False))
    sweep_pairs = long[long["unique_id"].isin(sweep_codes)].reset_index(drop=True)
    retail = backtest.windows("retail", main, calendar=True)
    sweep_base = backtest.windows("retail_sweep", sweep_pairs, calendar=False)
    sweep = [sweep_base.truncated(f"retail_sweep_L{n:02d}", n) for n in RETAIL_SWEEP]
    return retail, sweep


def grid_tasks(prepared: Path):
    frame = pd.read_parquet(prepared / "grid_halfhourly.parquet")
    backtest = GridBacktest(frame, GRID_HORIZON, GRID_CONTEXT, GRID_CONTEXT)
    historic_cutoffs = [c for start, days in GRID_HISTORIC_BLOCKS for c in midnights(start, days)]
    historic = backtest.windows("grid_historic", historic_cutoffs)
    leak_free = backtest.windows("grid_leakfree", midnights(*GRID_LEAK_FREE_DAYS))
    sweep_cutoffs = [midnights(start, days)[d] for start, days in GRID_HISTORIC_BLOCKS for d in GRID_SWEEP_DAYS]
    sweep_base = backtest.windows("grid_sweep", sweep_cutoffs).without_covariates("grid_sweep")
    sweep = [sweep_base.truncated(f"grid_sweep_L{n:04d}", n) for n in GRID_SWEEP]
    return backtest, historic, leak_free, sweep


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared", type=Path, default=Path("data/prepared"))
    parser.add_argument("--out", type=Path, default=Path("results/forecasts"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--only", nargs="*", help="contender names to run (default: all)")
    parser.add_argument("--products", type=int, default=RETAIL_PRODUCTS)
    parser.add_argument("--sweep-products", type=int, default=RETAIL_SWEEP_PRODUCTS)
    parser.add_argument(
        "--family", choices=["classical", "neural"], required=True,
        help="classical (statsforecast, LightGBM) and neural (torch) models run in separate processes: "
             "LightGBM's and torch's OpenMP runtimes crash each other on macOS",
    )
    parser.add_argument("--part", choices=["retail", "grid", "fresh", "all"], default="all")
    args = parser.parse_args()
    if args.family == "neural":
        import torch

        torch.set_num_threads(THREADS)
    run = Run(args.out, args.force, THREADS)

    neural = (C.Timestral, C.Chronos2, C.TimesFM25, C.TimesFM3, C.T0)

    def wanted(contender) -> bool:
        family = "neural" if isinstance(contender, neural) else "classical"
        return family == args.family and (not args.only or contender.name in args.only)

    if args.part in ("retail", "all"):
        retail, sweep = retail_tasks(args.prepared, args.products, args.sweep_products)
        plain = retail.without_covariates("retail")
        calendar = retail.named("retail_calendar")
        from statsforecast.models import TSB, AutoETS, CrostonOptimized

        jobs = [
            (C.SeasonalNaive("seasonal-naive", 52), [plain] + sweep),
            (C.Statistical("autoets", AutoETS(season_length=52), "AutoETS", "W-SUN", 1, True), [plain] + sweep),
            (C.Statistical("croston", CrostonOptimized(), "CrostonOptimized", "W-SUN", 1, False), [plain]),
            (C.Statistical("tsb", TSB(alpha_d=0.1, alpha_p=0.1), "TSB", "W-SUN", 1, False), [plain]),
            (C.RetailLightGBM("lightgbm", [1, 2, 3, 4, 8, 13, 26, 52], 200, LIGHTGBM_THREADS, SEED), [plain] + sweep),
            (C.Timestral("timestral-5m", REPOS["timestral-5m"], 64, False), [plain] + sweep),
            (C.Timestral("timestral-209m", REPOS["timestral-209m"], 64, False), [plain] + sweep),
            (C.Timestral("timestral-209m+calendar", REPOS["timestral-209m"], 64, True), [calendar]),
            (C.Chronos2("chronos-2", REPOS["chronos-2"], 256, False), [plain] + sweep),
            (C.TimesFM25("timesfm-2.5", REPOS["timesfm-2.5"], 128, 64), [plain] + sweep),
            (C.TimesFM3("timesfm-3", REPOS["timesfm-3"], 64, False), [plain] + sweep),
            (C.T0("t0-gamma", REPOS["t0-gamma"], 64, False), [plain] + sweep),
            (C.T0("t0-beta", REPOS["t0-beta"], 64, False), [plain]),
        ]
        for contender, tasks in jobs:
            if wanted(contender):
                run.execute(contender, tasks)

    if args.part in ("grid", "all"):
        backtest, historic, leak_free, sweep = grid_tasks(args.prepared)
        plain = [historic.without_covariates("grid_historic"), leak_free.without_covariates("grid_leakfree")]
        with_temperature = [historic.named("grid_historic_temp"), leak_free.named("grid_leakfree_temp")]
        from statsforecast.models import AutoETS

        lags = [48, 96, 144, 336, 672]
        jobs = [
            (C.SeasonalNaive("seasonal-naive", 336), plain + sweep),
            (C.Statistical("autoets", AutoETS(season_length=48), "AutoETS", "30min", THREADS, True), plain + sweep),
            (C.GridLightGBM("lightgbm", backtest, GRID_TRAINING_DAYS, lags, 200, LIGHTGBM_THREADS, SEED, False), plain),
            (C.GridLightGBM("lightgbm", backtest, GRID_TRAINING_DAYS, lags, 200, LIGHTGBM_THREADS, SEED, True), with_temperature),
            (C.GridLightGBM("lightgbm-context-only", backtest, None, lags, 200, LIGHTGBM_THREADS, SEED, False), sweep),
            (C.Timestral("timestral-5m", REPOS["timestral-5m"], 8, True), plain + with_temperature + sweep),
            (C.Timestral("timestral-209m", REPOS["timestral-209m"], 8, True), plain + with_temperature + sweep),
            (C.Chronos2("chronos-2", REPOS["chronos-2"], 64, True), plain + with_temperature + sweep),
            (C.TimesFM25("timesfm-2.5", REPOS["timesfm-2.5"], GRID_CONTEXT, 8), plain + sweep),
            (C.TimesFM3("timesfm-3", REPOS["timesfm-3"], 8, True), plain + with_temperature + sweep),
            (C.T0("t0-gamma", REPOS["t0-gamma"], 8, True), plain + with_temperature + sweep),
            (C.T0("t0-beta", REPOS["t0-beta"], 8, True), plain + with_temperature),
        ]
        for contender, tasks in jobs:
            if wanted(contender):
                run.execute(contender, tasks)

    if args.part in ("fresh", "all"):
        fresh, notes = FreshRetail(Path("data/raw/freshretailnet_train.parquet"),
                                   Path("data/raw/freshretailnet_eval.parquet")).windows("fresh", FRESH_SERIES, SEED)
        Path(args.prepared / "fresh_notes.json").write_text(json.dumps(notes, indent=2))
        plain = fresh.without_covariates("fresh")
        promo = fresh.named("fresh_promo")
        from statsforecast.models import AutoETS

        jobs = [
            (C.SeasonalNaive("seasonal-naive", 7), [plain]),
            (C.Statistical("autoets", AutoETS(season_length=7), "AutoETS", "D", 1, True), [plain]),
            (C.PanelLightGBM("lightgbm", [7, 14, 21, 28], 200, LIGHTGBM_THREADS, SEED, False), [plain]),
            (C.PanelLightGBM("lightgbm", [7, 14, 21, 28], 200, LIGHTGBM_THREADS, SEED, True), [promo]),
            (C.Timestral("timestral-209m", REPOS["timestral-209m"], 64, True), [plain, promo]),
            (C.Chronos2("chronos-2", REPOS["chronos-2"], 256, True), [plain, promo]),
            (C.TimesFM3("timesfm-3", REPOS["timesfm-3"], 64, True), [plain, promo]),
            (C.T0("t0-gamma", REPOS["t0-gamma"], 64, True), [plain, promo]),
        ]
        for contender, tasks in jobs:
            if wanted(contender):
                run.execute(contender, tasks)


if __name__ == "__main__":
    main()
