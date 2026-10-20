"""Score stored forecasts: per-window metrics, then GIFT-Eval-style aggregates per task and model."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from forecastbench import metrics
from forecastbench.metrics import LEVELS

MEDIAN = 4
LOW, HIGH, P90 = 0, 8, 8


class Task:
    """One task directory of stored forecasts."""

    def __init__(self, directory: Path):
        self._dir = directory

    @property
    def name(self) -> str:
        return self._dir.name

    def models(self) -> list[str]:
        return sorted(p.stem for p in self._dir.glob("*.npz"))

    def windows(self) -> pd.DataFrame:
        return pd.read_parquet(self._dir / "windows.parquet")

    def targets(self) -> np.ndarray:
        return np.load(self._dir / "targets.npy")

    def quantiles(self, model: str) -> np.ndarray:
        return np.load(self._dir / f"{model}.npz")["quantiles"].astype(float)

    def timings(self) -> dict:
        p = self._dir / "timings.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def failures(self) -> dict:
        p = self._dir / "failures.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def per_window(self) -> pd.DataFrame:
        meta = self.windows()
        y = self.targets()
        rows = []
        for model in self.models():
            q = self.quantiles(model)
            for i in range(len(meta)):
                t = y[i]
                ok = ~np.isnan(t)
                s = meta["scale"].iloc[i]
                ql = metrics.quantile_loss(t, q[i], LEVELS)
                short, excess = metrics.newsvendor(t, q[i, :, P90])
                mae = float(np.mean(np.abs(t[ok] - q[i, ok, MEDIAN])))
                rows.append({
                    "task": self.name, "model": model, "key": meta["key"].iloc[i],
                    "series": meta["series"].iloc[i], "cutoff": meta["cutoff"].iloc[i],
                    "context_length": int(meta["context_length"].iloc[i]),
                    "points": int(ok.sum()), "mae": mae,
                    "mase": mae / s if np.isfinite(s) and s > 0 else np.nan,
                    "wql": float(np.mean(ql) / np.sum(np.abs(t[ok]))) if np.sum(np.abs(t[ok])) > 0 else np.nan,
                    "abs_target": float(np.sum(np.abs(t[ok]))),
                    **{f"ql_{lv:.1f}": float(v) for lv, v in zip(LEVELS, ql)},
                    "covered": int(np.sum((t[ok] >= q[i, ok, LOW]) & (t[ok] <= q[i, ok, HIGH]))),
                    "short_p90": short, "excess_p90": excess,
                    "units": float(np.sum(t[ok])),
                })
        return pd.DataFrame(rows)


def bootstrap_ratio(model: np.ndarray, baseline: np.ndarray, groups: np.ndarray, reps: int, seed: int) -> list[float]:
    """95% interval of the geometric-mean ratio, resampling whole series (groups)."""
    ok = np.isfinite(model) & np.isfinite(baseline) & (model > 0) & (baseline > 0)
    logs = np.log(model[ok] / baseline[ok])
    g = groups[ok]
    names, inverse = np.unique(g, return_inverse=True)
    if len(names) < 2:
        return [float("nan"), float("nan")]
    sums = np.bincount(inverse, weights=logs)
    counts = np.bincount(inverse)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(names), size=(reps, len(names)))
    ratios = np.exp(sums[draws].sum(axis=1) / counts[draws].sum(axis=1))
    return [float(np.percentile(ratios, 2.5)), float(np.percentile(ratios, 97.5))]


def aggregate(scores: pd.DataFrame, baseline_scores: pd.DataFrame, baseline: str, reps: int, seed: int) -> pd.DataFrame:
    """One row per model: raw metrics, and ratios to the baseline model on the same windows."""
    base = baseline_scores[baseline_scores["model"] == baseline].set_index("key")
    rows = []
    for model, g in scores.groupby("model"):
        g = g.set_index("key")
        b = base.loc[g.index]
        ql_cols = [f"ql_{lv:.1f}" for lv in LEVELS]
        pooled = float(np.mean(g[ql_cols].sum().to_numpy() / g["abs_target"].sum()))
        pooled_base = float(np.mean(b[ql_cols].sum().to_numpy() / b["abs_target"].sum()))
        rel_mase, n_mase = metrics.geometric_mean_ratio(g["mase"].to_numpy(), b["mase"].to_numpy())
        rel_wql, n_wql = metrics.geometric_mean_ratio(g["wql"].to_numpy(), b["wql"].to_numpy())
        groups = g["series"].to_numpy() if g["series"].nunique() > 1 else g.index.to_numpy()
        rows.append({
            "model": model,
            "windows": int(len(g)),
            "series": int(g["series"].nunique()),
            "target_points": int(g["points"].sum()),
            "mase_mean": float(np.nanmean(g["mase"])),
            "mase_median": float(np.nanmedian(g["mase"])),
            "wql_pooled": pooled,
            "relative_mase_geomean": rel_mase,
            "relative_mase_ci95": bootstrap_ratio(g["mase"].to_numpy(), b["mase"].to_numpy(), groups, reps, seed),
            "relative_mase_pairs": n_mase,
            "relative_wql_pooled": pooled / pooled_base if pooled_base > 0 else float("nan"),
            "relative_wql_geomean": rel_wql,
            "relative_wql_pairs": n_wql,
            "coverage_10_90": float(g["covered"].sum() / g["points"].sum()),
            "units_short_at_p90": float(g["short_p90"].sum()),
            "units_excess_at_p90": float(g["excess_p90"].sum()),
            "units_demanded": float(g["units"].sum()),
        })
    return pd.DataFrame(rows)
