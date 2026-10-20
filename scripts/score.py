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
from forecastbench.scoring import Task, aggregate, bootstrap_mean_ratio, bootstrap_ratio, mean_ratio

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


RETAIL_RIVALS = ["lightgbm", "autoets", "chronos-2", "seasonal-naive"]
FLOOR_RIVALS = ["seasonal-naive", "lightgbm-transfer", "autoets", "chronos-2"]
GRID_PAIRS = [("_temp", "lightgbm-context-only", "_temp"), ("_temp", "theory-prior-2024", "_temp"),
              ("_temp", "theory-context", "_temp"), ("", "seasonal-naive", "")]


def head_to_head() -> list[tuple[str, str, str, str, str]]:
    """(task of model, model, task of rival, rival, label) for every comparison reported."""
    out = []
    retail = [("retail", "timestral-209m", "retail", r) for r in RETAIL_RIVALS]
    retail += [("retail_calendar", "timestral-209m+calendar", "retail", r) for r in ["timestral-209m"] + RETAIL_RIVALS]
    retail += [("fresh", "timestral-209m", "fresh", r) for r in ["lightgbm", "autoets", "chronos-2", "seasonal-naive"]]
    retail += [("fresh_promo", "timestral-209m", "fresh_promo", "lightgbm"),
               ("fresh_promo", "timestral-209m", "fresh", "timestral-209m")]
    for n in [8, 13, 26, 52, 78]:
        t = f"retail_sweep_L{n:02d}"
        retail += [(t, "timestral-209m", t, r) for r in RETAIL_RIVALS]
    for prefix in ["retail_floor_L", "retail300_floor_L"]:
        for n in [1, 2, 4, 8]:
            t = f"{prefix}{n:02d}"
            for model in ["timestral-209m", "timestral-5m"]:
                retail += [(t, model, t, r) for r in FLOOR_RIVALS]
    out += retail
    for n in [12, 24, 48, 96, 144, 336]:
        t = f"grid_floor_L{n:04d}"
        for model in ["timestral-209m", "timestral-5m"]:
            out += [(t + ma, model, t + ra, rival) for ma, rival, ra in GRID_PAIRS]
    return out


def tag(task: str, model: str) -> str:
    if task.endswith("_temp"):
        return model + "+temperature"
    if task == "fresh_promo":
        return model + "+promo"
    return model


def pairs(scores: dict) -> list[dict]:
    """Head-to-head MASE ratios on the same windows: ratio of means and geometric mean, with series-bootstrap CIs."""
    out = []
    for mt, model, rt, rival in head_to_head():
        a, b = scores.get(mt), scores.get(rt)
        entry = {"task": mt.replace("_temp", ""), "model": tag(mt, model), "rival": tag(rt, rival)}
        if a is None or b is None or model not in set(a["model"]) or rival not in set(b["model"]):
            out.append({**entry, "ratio_of_mean_mase": None, "ratio": None,
                        "note": "rival or model has no forecasts here (cannot fit or not run)"})
            continue
        x = a[a["model"] == model].set_index("key")
        y = b[b["model"] == rival].set_index("key").loc[x.index]
        groups = x["series"].to_numpy() if x["series"].nunique() > 1 else x.index.to_numpy()
        xm, ym = x["mase"].to_numpy(), y["mase"].to_numpy()
        means, n = mean_ratio(xm, ym)
        geo, ngeo = geometric_mean_ratio(xm, ym)
        out.append({**entry, "ratio_of_mean_mase": means, "pairs": n,
                    "ratio_of_mean_mase_ci95": bootstrap_mean_ratio(xm, ym, groups, BOOTSTRAP_REPS, SEED),
                    "ratio": geo, "geometric_pairs": ngeo,
                    "ci95": bootstrap_ratio(xm, ym, groups, BOOTSTRAP_REPS, SEED)})
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
        "head_to_head": summary_pairs,
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
