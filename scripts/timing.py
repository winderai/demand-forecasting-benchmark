"""Optional timing pass: every model on a fixed small workload, three repeats, load average recorded.

The backtest's own timings (in results/summary.json) were taken on a shared machine. This pass
waits for the 1-minute load average to fall below --max-load (up to --wait minutes), then times
each model on 256 retail windows and the 5 leak-free grid windows, without covariates, and
writes results/timing_<family>.json. Run it once per family, like run.py.
"""

import argparse
import json
import os
import platform
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))

import run as backtest  # noqa: E402

from forecastbench import contenders as C  # noqa: E402

REPEATS = 3
RETAIL_WINDOWS = 256


def subset(windows, n):
    from dataclasses import replace

    pick = list(range(min(n, len(windows))))
    return replace(
        windows,
        ids=[windows.ids[i] for i in pick], cutoffs=[windows.cutoffs[i] for i in pick],
        contexts=[windows.contexts[i] for i in pick], targets=windows.targets[pick],
        target_dates=[windows.target_dates[i] for i in pick], history=[windows.history[i] for i in pick],
        known=None, known_names=[],
        context_dates=None if windows.context_dates is None else [windows.context_dates[i] for i in pick],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=["classical", "neural"], required=True)
    parser.add_argument("--max-load", type=float, default=1.5)
    parser.add_argument("--wait", type=float, default=30.0)
    args = parser.parse_args()
    deadline = time.time() + args.wait * 60
    while os.getloadavg()[0] > args.max_load and time.time() < deadline:
        time.sleep(15)
    retail, _ = backtest.retail_tasks(Path("data/prepared"), backtest.RETAIL_PRODUCTS, backtest.RETAIL_SWEEP_PRODUCTS)
    grid_backtest, _, leak_free, _ = backtest.grid_tasks(Path("data/prepared"))
    small_retail = subset(retail.without_covariates("timing_retail"), RETAIL_WINDOWS)
    small_grid = leak_free.without_covariates("timing_grid")
    if args.family == "neural":
        import torch

        torch.set_num_threads(backtest.THREADS)
        repos = backtest.REPOS
        models = [
            (C.Timestral("timestral-5m", repos["timestral-5m"], 64, False), C.Timestral("timestral-5m", repos["timestral-5m"], 8, False)),
            (C.Timestral("timestral-209m", repos["timestral-209m"], 64, False), C.Timestral("timestral-209m", repos["timestral-209m"], 8, False)),
            (C.Chronos2("chronos-2", repos["chronos-2"], 256, False), C.Chronos2("chronos-2", repos["chronos-2"], 64, False)),
            (C.TimesFM25("timesfm-2.5", repos["timesfm-2.5"], 128, 64), C.TimesFM25("timesfm-2.5", repos["timesfm-2.5"], 4096, 8)),
            (C.TimesFM3("timesfm-3", repos["timesfm-3"], 64, False), C.TimesFM3("timesfm-3", repos["timesfm-3"], 8, False)),
            (C.T0("t0-gamma", repos["t0-gamma"], 64, False), C.T0("t0-gamma", repos["t0-gamma"], 8, False)),
        ]
    else:
        from statsforecast.models import AutoETS

        models = [
            (C.Statistical("autoets", AutoETS(season_length=52), "AutoETS", "W-SUN", 1, True),
             C.Statistical("autoets", AutoETS(season_length=48), "AutoETS", "30min", 1, True)),
            (C.RetailLightGBM("lightgbm", [1, 2, 3, 4, 8, 13, 26, 52], 200, 1, backtest.SEED),
             C.GridLightGBM("lightgbm", grid_backtest, backtest.GRID_TRAINING_DAYS, [48, 96, 144, 336, 672], 200, 1,
                            backtest.SEED, False)),
        ]
    rows = []
    for retail_model, grid_model in models:
        for model, windows in ((retail_model, small_retail), (grid_model, small_grid)):
            load = model.load()
            seconds = []
            before = os.getloadavg()[0]
            for _ in range(REPEATS):
                start = time.perf_counter()
                model.forecast(windows)
                seconds.append(time.perf_counter() - start)
            rows.append({
                "model": model.name, "task": windows.name, "windows": len(windows), "load_s": load,
                "median_s": float(np.median(seconds)), "median_s_per_window": float(np.median(seconds)) / len(windows),
                "repeats_s": seconds, "loadavg_1min_before": before, "loadavg_1min_after": os.getloadavg()[0],
            })
            print(rows[-1], flush=True)
    out = {
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
        "machine": f"{platform.machine()}, {os.cpu_count()} cores",
        "torch_threads": backtest.THREADS if args.family == "neural" else None,
        "statsforecast_jobs": 1, "lightgbm_threads": 1,
        "note": "AutoETS on the grid fits one series per window with n_jobs=1 here (the backtest used 8 processes).",
        "rows": rows,
    }
    Path(f"results/timing_{args.family}.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
