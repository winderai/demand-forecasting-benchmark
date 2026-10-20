"""Stage 4: score every stored forecast; write per-window metrics and results/summary.json."""

import argparse
import json
import os
import platform
import re
import subprocess
from importlib import metadata
from pathlib import Path

import pandas as pd

from forecastbench.scoring import Task, aggregate

BASELINE = "seasonal-naive"
BOOTSTRAP_REPS = 2000
SEED = 2026
POINT_ONLY = {"seasonal-naive", "croston", "tsb"}
PACKAGES = ["timestral", "chronos-forecasting", "timesfm", "tfc-t0", "statsforecast", "mlforecast", "lightgbm",
            "torch", "numpy", "pandas"]
REPOS = {
    "timestral-5m": "mistralai/Timestral-5M",
    "timestral-209m": "mistralai/Timestral-209M",
    "chronos-2": "amazon/chronos-2",
    "timesfm-2.5": "google/timesfm-2.5-200m-pytorch",
    "timesfm-3": "google/timesfm-3.0-pytorch",
    "t0-gamma": "theforecastingcompany/t0-gamma",
    "t0-beta": "theforecastingcompany/t0-beta",
}


def baseline_task(name: str) -> str:
    if name.startswith("retail_sweep_"):
        return "retail_sweep_L78"
    if name.startswith("grid_sweep_"):
        return "grid_sweep_L4032"
    return {"retail_calendar": "retail", "grid_historic_temp": "grid_historic",
            "grid_leakfree_temp": "grid_leakfree"}.get(name, name)


def snapshot(repo: str) -> str:
    cache = Path.home() / ".cache/huggingface/hub" / f"models--{repo.replace('/', '--')}" / "refs/main"
    return cache.read_text().strip() if cache.exists() else "unknown"


def environment() -> dict:
    lock = Path("uv.lock").read_text()
    found = re.search(r"timestral\.git\?rev=[0-9a-f]+#([0-9a-f]{40})", lock)
    commit = found.group(1) if found else "unknown"
    return {
        "machine": f"{platform.machine()} {subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True).stdout.strip()}, "
                   f"{os.cpu_count()} cores, "
                   f"{int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout) // 2**30} GB",
        "os": platform.platform(),
        "python": platform.python_version(),
        "device": "cpu",
        "packages": {p: metadata.version(p) for p in PACKAGES},
        "timestral_git_commit": commit,
        "model_snapshots": {name: {"repo": repo, "revision": snapshot(repo)} for name, repo in REPOS.items()},
        "benchmark_git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecasts", type=Path, default=Path("results/forecasts"))
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()
    tasks = {p.name: Task(p) for p in sorted(args.forecasts.iterdir()) if p.is_dir()}
    scores = {name: task.per_window() for name, task in tasks.items()}
    per_window = pd.concat(scores.values(), ignore_index=True)
    per_window.to_parquet(args.out / "metrics_per_window.parquet", index=False)
    per_window.drop(columns=[c for c in per_window.columns if c.startswith("ql_")]).to_csv(
        args.out / "metrics_per_window.csv.gz", index=False)
    tables = {}
    for name, task in tasks.items():
        if scores[name].empty:
            continue
        base = baseline_task(name)
        table = aggregate(scores[name], scores[base], BASELINE, BOOTSTRAP_REPS, SEED)
        timings = task.timings()
        table["load_s"] = table["model"].map(lambda m: timings.get(m, {}).get("load_s"))
        table["forecast_s"] = table["model"].map(lambda m: timings.get(m, {}).get("forecast_s"))
        table["s_per_window"] = table["model"].map(lambda m: timings.get(m, {}).get("s_per_window"))
        table["loadavg_1min_before"] = table["model"].map(lambda m: timings.get(m, {}).get("loadavg_1min_before"))
        table["point_only"] = table["model"].isin(POINT_ONLY)
        for col in ["coverage_10_90", "units_short_at_p90", "units_excess_at_p90"]:
            table.loc[table["point_only"], col] = None
        table = table.sort_values("relative_mase_geomean")
        tables[name] = {
            "baseline": f"{BASELINE} on task {base}",
            "rows": json.loads(table.to_json(orient="records")),
            "failures": task.failures(),
        }
    summary = {
        "run_date_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
        "environment": environment(),
        "data": json.loads(Path("data/manifest.json").read_text()),
        "data_notes": {
            "retail": json.loads(Path("data/prepared/retail_notes.json").read_text()),
            "grid": json.loads(Path("data/prepared/grid_notes.json").read_text()),
        },
        "conventions": {
            "point_forecast": "median (quantile 0.5) for every model",
            "mase": "MAE of the median over the mean absolute seasonal difference of the in-sample history; "
                    "period 1 for weekly retail, 48 for half-hourly grid (GIFT-Eval / GluonTS seasonality). "
                    "Sweep tasks scale every truncation by the same full history.",
            "wql": "mean over levels 0.1..0.9 of 2 * sum(pinball loss) / sum(|y|) (GIFT-Eval CRPS proxy). "
                   "wql_pooled sums over every window of a task, as GIFT-Eval does per dataset.",
            "relative": "relative_mase_geomean: geometric mean over windows of model MASE / seasonal-naive MASE, "
                        "skipping pairs where either is zero; CI from a series-level bootstrap. "
                        "relative_wql_pooled: pooled WQL over pooled seasonal-naive WQL.",
            "point_only_models": sorted(POINT_ONLY) + [" have nine identical quantiles: their WQL is the "
                                                       "point forecast's, and coverage and the p90 order are not reported"],
            "newsvendor": "order each week at the 90th-percentile forecast (optimal only if a unit short costs 9x a "
                          "unit left over); units short and units left over, summed over all windows",
            "retail_clip": "every retail quantile clipped at zero, for every contender",
        },
        "tasks": tables,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"scored {len(tasks)} tasks, {len(per_window)} window-model rows")


if __name__ == "__main__":
    main()
