"""Sanity checks on the stored forecasts; writes results/sanity.json.

1. Timestral's README example returns the shapes the README states.
2. The batched, left-padded Timestral run matches a direct single-series call on the same windows.
3. Every stored forecast is finite and has ordered quantiles; crossings before sorting are reported.
4. Seasonal naive reproduces the value one season back.
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import torch  # noqa: E402
from statsforecast.models import AutoETS  # noqa: E402
from timestral import TimestralForecaster  # noqa: E402

from forecastbench.scoring import Task  # noqa: E402
from forecastbench.windows import christmas_covariates  # noqa: E402

CHECK_WINDOWS = [0, 100, 500, 1000, 1300]


def main() -> None:
    torch.set_num_threads(8)
    out = {}
    model = TimestralForecaster.from_pretrained("mistralai/Timestral-209M", local_files_only=True)
    context = np.random.randn(2, 1, 2000).cumsum(-1)
    f = model.forecast(context, prediction_length=96)
    out["readme_example"] = {
        "quantiles_shape": list(f.quantiles.shape), "readme_says": [2, 1, 96, 21],
        "quantile_levels": [round(q, 2) for q in f.quantile_levels], "median_shape": list(f.median.shape),
    }

    task = Task(Path("results/forecasts/retail"))
    meta = task.windows()
    stored = task.quantiles("timestral-209m")
    weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
    diffs = []
    for i in CHECK_WINDOWS:
        if i >= len(meta):
            continue
        s = weekly[weekly["unique_id"] == meta.loc[i, "series"]]
        ctx = s[s["ds"] <= pd.Timestamp(meta.loc[i, "cutoff"])]["y"].to_numpy()
        direct = model.forecast(ctx, prediction_length=8).quantiles[0, 0].numpy()
        levels = list(model.quantile_levels)
        pick = [min(range(len(levels)), key=lambda j: abs(levels[j] - q)) for q in np.arange(0.1, 1.0, 0.1)]
        d = np.clip(direct[:, pick], 0, None)
        diffs.append({"window": i, "series": meta.loc[i, "series"], "context_length": int(len(ctx)),
                      "max_abs_diff_median": float(np.max(np.abs(d[:, 4] - stored[i, :, 4]))),
                      "median_scale": float(np.mean(np.abs(d[:, 4])))})
    out["batched_vs_direct_timestral_209m"] = diffs

    finite = {}
    for directory in sorted(Path("results/forecasts").iterdir()):
        if not directory.is_dir():
            continue
        t = Task(directory)
        timings = t.timings()
        for m in t.models():
            q = t.quantiles(m)
            finite[f"{directory.name}/{m}"] = {
                "nan": int(np.isnan(q).sum()), "ordered": bool((np.diff(q, axis=-1) >= -1e-6).all()),
                "crossings_before_sort": timings.get(m, {}).get("quantile_crossings_before_sort"),
            }
    out["forecasts"] = finite

    snaive = task.quantiles("seasonal-naive")
    rows = []
    for i in CHECK_WINDOWS:
        if i >= len(meta):
            continue
        s = weekly[weekly["unique_id"] == meta.loc[i, "series"]].reset_index(drop=True)
        n = int(meta.loc[i, "context_length"])
        expected = s["y"].to_numpy()[n - 52:n - 44] if n >= 52 else np.repeat(s["y"].to_numpy()[n - 1], 8)
        rows.append({"window": i, "matches": bool(np.allclose(expected, snaive[i, :, 4]))})
    out["seasonal_naive_retail"] = rows
    # Timestral with a known-future indicator that never fires in the context (product 23155,
    # 29 weeks of history at the 9 Oct 2011 cut-off; the Nov-Dec flag turns on in week 4 of 8).
    s = weekly[weekly["unique_id"] == "23155"]
    ds = pd.DatetimeIndex(s["ds"])
    y = s["y"].to_numpy(dtype=float)
    n = int((ds <= pd.Timestamp("2011-10-09")).sum())
    k = christmas_covariates(ds[: n + 8])
    rows = {}
    for name, rows_k in [("none", None), ("peak_flag_and_week", k[None]), ("peak_flag_only", k[None, :1]),
                         ("week_of_year_only", k[None, 1:])]:
        f = model.forecast(y[:n], prediction_length=8, known_covariates=rows_k)
        rows[name] = {"median": np.round(f.quantile(0.5)[0, 0].numpy()).tolist(),
                      "p90": np.round(f.quantile(0.9)[0, 0].numpy()).tolist()}
    out["timestral_unseen_indicator_23155"] = {"context_weeks": n, "actual": y[n:n + 8].tolist(), **rows}

    longest = meta.sort_values("context_length", ascending=False).head(20)
    components = []
    for i in longest.index:
        s = weekly[weekly["unique_id"] == meta.loc[i, "series"]]
        ctx = s[s["ds"] <= pd.Timestamp(meta.loc[i, "cutoff"])]["y"].to_numpy(dtype=float)
        components.append(AutoETS(season_length=52).fit(ctx).model_["components"])
    out["autoets_retail_components_20_longest"] = {
        "context_lengths": sorted({int(x) for x in longest["context_length"]}),
        "components": {c: components.count(c) for c in set(components)},
    }
    Path("results/sanity.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "forecasts"}, indent=2))
    bad = {k: v for k, v in finite.items() if v["nan"] or not v["ordered"]}
    print(f"{len(finite)} stored forecasts checked, {len(bad)} with NaN or crossing quantiles")


if __name__ == "__main__":
    main()
