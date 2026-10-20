"""Stage 4: score every stored forecast; write per-window metrics and results/summary.json."""

import argparse
import json

import os
import platform
import re
import subprocess
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

from forecastbench.metrics import geometric_mean_ratio
from forecastbench.scoring import Task, aggregate, bootstrap_ratio

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
    if name.startswith("grid_floor_"):
        return "grid_floor_L0336"
    if name.startswith("retail_floor_"):
        return "retail_sweep_L78"
    if name.startswith("retail300_floor_"):
        return "retail"
    if name.startswith("extrap_"):
        return name.replace("_temp", "")
    if name.startswith("retail_sweep_"):
        return "retail_sweep_L78"
    if name.startswith("grid_sweep_"):
        return "grid_sweep_L4032"
    return {"retail_calendar": "retail", "grid_historic_temp": "grid_historic",
            "grid_leakfree_temp": "grid_leakfree", "fresh_promo": "fresh"}.get(name, name)


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


PAIRS = {
    "grid": [("timestral-209m", "_temp", "lightgbm-context-only", "_temp"),
             ("timestral-209m", "_temp", "theory-prior-2024", "_temp"),
             ("timestral-209m", "_temp", "theory-context", "_temp"),
             ("timestral-209m", "", "seasonal-naive", ""),
             ("timestral-5m", "_temp", "lightgbm-context-only", "_temp"),
             ("timestral-5m", "_temp", "theory-prior-2024", "_temp"),
             ("timestral-5m", "_temp", "theory-context", "_temp"),
             ("timestral-5m", "", "seasonal-naive", "")],
    "retail": [("timestral-209m", "", "seasonal-naive", ""), ("timestral-209m", "", "lightgbm-transfer", ""),
               ("timestral-5m", "", "seasonal-naive", ""), ("timestral-5m", "", "lightgbm-transfer", "")],
}


def pairs(scores: dict) -> list[dict]:
    """Head-to-head geometric-mean MASE ratios on the same windows, with a bootstrap 95% interval."""
    out = []
    for name in sorted(scores):
        kind = "grid" if name.startswith("grid_floor_") and not name.endswith("_temp") else (
            "retail" if "_floor_" in name and not name.startswith("grid") else None)
        if kind is None:
            continue
        for model, ma, rival, ra in PAIRS[kind]:
            a = scores.get(name + ma)
            b = scores.get(name + ra)
            if a is None or b is None or model not in set(a["model"]) or rival not in set(b["model"]):
                out.append({"task": name, "model": model + ma, "rival": rival + ra, "ratio": None,
                            "note": "rival or model has no forecasts at this length (cannot fit)"})
                continue
            x = a[a["model"] == model].set_index("key")["mase"]
            y = b[b["model"] == rival].set_index("key")["mase"].loc[x.index]
            groups = a[a["model"] == model].set_index("key")["series"].loc[x.index].to_numpy()
            if len(set(groups)) < 2:
                groups = x.index.to_numpy()
            ratio, n = geometric_mean_ratio(x.to_numpy(), y.to_numpy())
            out.append({"task": name, "model": model + ma.replace("_temp", "+temperature"),
                        "rival": rival + ra.replace("_temp", "+temperature"), "ratio": ratio, "pairs": n,
                        "ratio_of_mean_mase": float(np.nanmean(x.to_numpy()) / np.nanmean(y.to_numpy())),
                        "ci95": bootstrap_ratio(x.to_numpy(), y.to_numpy(), groups, BOOTSTRAP_REPS, SEED)})
    return out


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
        same = name.replace("_temp", "")
        if (name.startswith("grid_floor_") or "_floor_" in name) and same in scores:
            local = aggregate(scores[name], scores[same], BASELINE, BOOTSTRAP_REPS, SEED).set_index("model")
            table["relative_mase_vs_same_length_naive"] = table["model"].map(local["relative_mase_geomean"])
            table["relative_mase_vs_same_length_naive_ci95"] = table["model"].map(local["relative_mase_ci95"])
        table = table.sort_values("relative_mase_geomean")
        tables[name] = {
            "baseline": f"{BASELINE} on task {base}",
            "rows": json.loads(table.to_json(orient="records")),
            "failures": task.failures(),
        }
    summary_pairs = pairs(scores)
    summary = {
        "floor_pairs": summary_pairs,
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
        "timing_pass": {f.stem: json.loads(f.read_text()) for f in sorted(args.out.glob("timing_*.json"))},
        "sanity": json.loads((args.out / "sanity.json").read_text()) if (args.out / "sanity.json").exists() else None,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"scored {len(tasks)} tasks, {len(per_window)} window-model rows")


if __name__ == "__main__":
    main()
