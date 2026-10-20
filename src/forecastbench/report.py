"""Charts (SVG + PNG) and the compact demo.json for the article's interactive chart."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from forecastbench.scoring import Task  # noqa: E402

LABELS = {
    "seasonal-naive": "Seasonal naive",
    "autoets": "AutoETS (spreadsheet stand-in)",
    "ets-aaa": "ETS(A,A,A) (Excel FORECAST.ETS structure)",
    "croston": "Croston (optimised)",
    "tsb": "TSB",
    "lightgbm": "LightGBM (global, fitted)",
    "lightgbm-context-only": "LightGBM (fitted on the context only)",
    "timestral-5m": "Timestral 5M",
    "timestral-209m": "Timestral 209M",
    "timestral-209m+calendar": "Timestral 209M + calendar covariates",
    "chronos-2": "Chronos-2",
    "timesfm-2.5": "TimesFM 2.5",
    "timesfm-3": "TimesFM 3 (non-commercial weights)",
    "t0-gamma": "t0-gamma",
    "t0-beta": "t0-beta",
    "theory-context": "Theory model, fitted on the context",
    "theory-prior-2024": "Theory model, structure from 2024",
    "lightgbm-transfer": "LightGBM (trained on 600 other products)",
    "lightgbm-no-lags": "LightGBM (calendar, no lags)",
}
FITTED = {"autoets", "ets-aaa", "theory-context", "theory-prior-2024", "lightgbm-transfer", "lightgbm-no-lags", "croston", "tsb", "lightgbm", "lightgbm-context-only"}
BASELINES = {"seasonal-naive"}
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
COLOURS = {"baseline": "#8a8984", "fitted": "#eb6834", "pretrained": "#2a78d6"}
LINES = {
    "seasonal-naive": "#8a8984", "autoets": "#eb6834", "lightgbm": "#4a3aa7", "lightgbm-context-only": "#4a3aa7",
    "timestral-209m": "#2a78d6", "timestral-5m": "#1baf7a", "chronos-2": "#e87ba4", "t0-gamma": "#008300",
    "timesfm-3": "#eda100", "timesfm-2.5": "#e34948", "ets-aaa": "#8a5a00",
}
SWEEP_MODELS = ["seasonal-naive", "autoets", "ets-aaa", "lightgbm", "lightgbm-context-only", "timestral-5m", "timestral-209m",
                "chronos-2", "timesfm-2.5", "timesfm-3", "t0-gamma"]


def label(model: str) -> str:
    if model in LABELS:
        return LABELS[model]
    base, _, extra = model.partition("+")
    extras = {"temperature": "+ temperature", "promo": "+ discount, holiday, activity"}
    return f"{LABELS.get(base, base)} {extras.get(extra, '+ ' + extra)}"


def family(model: str) -> str:
    base = model.split("+")[0]
    if base in BASELINES:
        return "baseline"
    return "fitted" if base in FITTED else "pretrained"


def style(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".svg"), facecolor="white", bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), facecolor="white", bbox_inches="tight", dpi=160)
    plt.close(fig)


class Summary:
    def __init__(self, path: Path):
        self._data = json.loads(path.read_text())

    def table(self, task: str) -> pd.DataFrame:
        return pd.DataFrame(self._data["tasks"][task]["rows"]) if task in self._data["tasks"] else pd.DataFrame()

    def merged(self, plain: str, covariate: str) -> pd.DataFrame:
        """Plain task rows plus the covariate task's rows, renamed model+temperature."""
        a = self.table(plain)
        b = self.table(covariate)
        if not b.empty:
            b = b.assign(model=b["model"] + "+temperature")
        return pd.concat([a, b], ignore_index=True)

    @property
    def machine(self) -> str:
        return self._data["environment"]["machine"]


def bars(summary: Summary, out: Path) -> None:
    panels = [
        ("Retail: 300 products, 5 cut-offs, 8 weeks ahead", summary.table("retail")),
        ("GB demand 2025: 28 days, day ahead", summary.merged("grid_historic", "grid_historic_temp")),
        ("GB demand after 15 Oct 2026 (leak-free): 5 days", summary.merged("grid_leakfree", "grid_leakfree_temp")),
    ]
    metrics = [("relative_mase_geomean", "MASE relative to seasonal naive"),
               ("relative_wql_pooled", "WQL relative to seasonal naive")]
    heights = [max(len(t), 1) for _, t in panels]
    fig, axes = plt.subplots(len(panels), 2, figsize=(11, 0.28 * sum(heights) + 2.5),
                             gridspec_kw={"height_ratios": heights}, squeeze=False)
    for r, (title, table) in enumerate(panels):
        for c, (metric, xlabel) in enumerate(metrics):
            ax = axes[r][c]
            style(ax)
            if table.empty:
                ax.set_visible(False)
                continue
            t = table.sort_values("relative_mase_geomean", ascending=False)
            y = np.arange(len(t))
            values = t[metric].to_numpy(dtype=float)
            ax.barh(y, values, height=0.7, color=[COLOURS[family(m)] for m in t["model"]], edgecolor="white", linewidth=1)
            if metric == "relative_mase_geomean":
                lo = np.array([ci[0] for ci in t["relative_mase_ci95"]], dtype=float)
                hi = np.array([ci[1] for ci in t["relative_mase_ci95"]], dtype=float)
                ok = np.isfinite(lo) & np.isfinite(hi)
                ax.errorbar(values[ok], y[ok], xerr=[values[ok] - lo[ok], hi[ok] - values[ok]], fmt="none",
                            ecolor=INK, elinewidth=0.8, capsize=2)
            ends = values.copy()
            if metric == "relative_mase_geomean":
                ends = np.where(np.isfinite(hi), np.maximum(values, hi), values)
            for yi, v, e in zip(y, values, ends):
                if np.isfinite(v):
                    ax.text(e, yi, f"  {v:.2f}", va="center", fontsize=7, color=INK)
            ax.axvline(1.0, color=MUTED, linewidth=0.8, linestyle="--")
            ax.set_yticks(y)
            ax.set_yticklabels([label(m) for m in t["model"]] if c == 0 else [], fontsize=8, color=INK)
            ax.set_xlabel(xlabel, fontsize=8, color=MUTED)
            if c == 0:
                ax.set_title(title, loc="left", fontsize=10, color=INK)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOURS[k]) for k in ("baseline", "fitted", "pretrained")]
    fig.legend(handles, ["Baseline", "Fitted per cut-off", "Pretrained (zero-shot)"], loc="lower center", ncol=3,
               frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.025))
    fig.text(0.01, 0.002, "Lower is better. MASE: geometric mean over windows of the ratio to seasonal naive, with "
             "95% series-bootstrap intervals. WQL: pooled. Temperature is the day's measured GB average (an oracle).",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, out / "results_bars")


def sweep_curves(summary: Summary, prefix: str, lengths: list[int]) -> dict:
    curves = {"relmase": {}, "relwql": {}, "mase": {}, "n_windows": None, "n_series": None}
    for n in lengths:
        t = summary.table(f"{prefix}{n:02d}" if prefix.startswith("retail") else f"{prefix}{n:04d}")
        if t.empty:
            continue
        curves["n_windows"] = int(t["windows"].max())
        curves["n_series"] = int(t["series"].max())
        for _, row in t.iterrows():
            curves["relmase"].setdefault(row["model"], {})[n] = row["relative_mase_geomean"]
            curves["relwql"].setdefault(row["model"], {})[n] = row["relative_wql_pooled"]
            curves["mase"].setdefault(row["model"], {})[n] = row["mase_mean"]
    return curves


def sweep_chart(curves: dict, lengths: list[int], unit: str, title: str, path: Path, ticks: list[str],
                footnote: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, key, ylabel in zip(axes, ["relmase", "relwql"],
                               ["MASE relative to seasonal naive (full history)", "WQL relative to seasonal naive"]):
        style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        for model in SWEEP_MODELS:
            if model not in curves[key]:
                continue
            xs = [n for n in lengths if n in curves[key][model]]
            ys = [curves[key][model][n] for n in xs]
            dashed = family(model) == "fitted"
            ax.plot(xs, ys, color=LINES.get(model, INK), linewidth=2, marker="o", markersize=5,
                    linestyle="--" if dashed else "-", label=label(model))
        ax.set_xscale("log")
        if key == "relwql":
            ax.set_yscale("log")
            ax.set_yticks([0.5, 0.7, 1, 2, 5, 10])
            ax.set_yticklabels(["0.5", "0.7", "1", "2", "5", "10"], fontsize=8)
            ax.minorticks_off()
        ax.set_xticks(lengths)
        ax.set_xticklabels(ticks, fontsize=8)
        ax.minorticks_off()
        ax.set_xlabel(f"History given to every model ({unit})", fontsize=8, color=MUTED)
        ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
    axes[0].set_title(title, loc="left", fontsize=10, color=INK)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.04))
    fig.text(0.01, 0.005, footnote, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    save(fig, path)


def example_chart(forecasts: Path, products: pd.DataFrame, out: Path, series: str, cutoff: str, models: list[str]) -> None:
    task = Task(forecasts / "retail")
    meta = task.windows()
    hit = meta.index[(meta["series"] == series) & (meta["cutoff"].str.startswith(cutoff))]
    if len(hit) == 0:
        return
    i = int(hit[0])
    weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
    s = weekly[weekly["unique_id"] == series].set_index("ds")["y"]
    cut = pd.Timestamp(cutoff)
    target_dates = s.index[s.index > cut][:8]
    fig, axes = plt.subplots(1, len(models), figsize=(4 * len(models), 3.4), sharey=True)
    name = products.set_index("StockCode")["description"].get(series, series)
    for ax, model in zip(np.atleast_1d(axes), models):
        style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        q = task.quantiles(model)[i]
        ax.plot(s.index[s.index <= cut][-40:], s[s.index <= cut][-40:], color=MUTED, linewidth=1.5, label="History")
        ax.fill_between(target_dates, q[:, 0], q[:, 8], color=LINES.get(model, "#2a78d6"), alpha=0.25, linewidth=0,
                        label="10-90% band")
        ax.plot(target_dates, q[:, 4], color=LINES.get(model, "#2a78d6"), linewidth=2, label="Median")
        ax.plot(target_dates, task.targets()[i], color=INK, linewidth=0, marker="o", markersize=4, label="Actual")
        ax.set_title(label(model), loc="left", fontsize=9, color=INK)
        ax.tick_params(axis="x", rotation=45)
    np.atleast_1d(axes)[0].set_ylabel("Units per week", fontsize=8, color=MUTED)
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.suptitle(f"{name.title()} ({series}), cut-off week ending {cutoff}", x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    save(fig, out / "example_forecast")


def sig(x: float, digits: int = 3):
    if x is None or not np.isfinite(x):
        return None
    if x == 0:
        return 0
    return float(f"{x:.{digits}g}")


def demo(forecasts: Path, summary: Summary, products: pd.DataFrame, picks: list[dict], grid_week: list[str],
         sweep: dict, lengths: list[int], out: Path) -> None:
    weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
    names = products.set_index("StockCode")["description"]
    retail = Task(forecasts / "retail")
    meta = retail.windows()
    targets = retail.targets()
    retail_models = [m for m in retail.models()]
    cache = {m: retail.quantiles(m) for m in retail_models}
    series = []
    for pick in picks:
        code = pick["code"]
        s = weekly[weekly["unique_id"] == code].set_index("ds")["y"]
        rows = meta.index[meta["series"] == code]
        cutoffs = []
        for i in rows[meta.loc[rows, "cutoff"].isin([c + "T00:00:00" for c in pick["cutoffs"]])]:
            cut = pd.Timestamp(meta.loc[i, "cutoff"])
            dates = s.index[s.index > cut][:8]
            cutoffs.append({
                "cutoff": cut.date().isoformat(), "leak_free": False,
                "t": [d.date().isoformat() for d in dates],
                "actual": [int(v) for v in targets[i]],
                "forecasts": {m: {f"q{k}": [sig(v) for v in cache[m][i, :, j]] for k, j in (("10", 0), ("50", 4), ("90", 8))}
                              for m in retail_models},
            })
        series.append({
            "id": f"retail-{code}", "label": f"{names.get(code, code).strip().capitalize()} ({pick['role']})",
            "kind": "retail", "freq": "W", "note": pick["note"],
            "history": {"t": [d.date().isoformat() for d in s.index], "y": [int(v) for v in s.to_numpy()]},
            "cutoffs": cutoffs,
        })
    grid = pd.read_parquet("data/prepared/grid_halfhourly.parquet").set_index("ds")
    for task_name, cov_name, days, leak, sid, lab, note in [
        ("grid_historic", "grid_historic_temp", grid_week, False, "grid-nd-2025",
         "GB national demand, one week of July 2025", "Historic week; old public data that models may have seen in training"),
        ("grid_leakfree", "grid_leakfree_temp", None, True, "grid-nd",
         "GB national demand after Timestral's release", "Leak-free: every target is after 15 Oct 2026 00:00 UK time"),
    ]:
        plain = Task(forecasts / task_name)
        cov = Task(forecasts / cov_name)
        m = plain.windows()
        idx = list(m.index) if days is None else [i for i in m.index if m.loc[i, "cutoff"][:10] in days]
        qs = {name: plain.quantiles(name) for name in plain.models()}
        qs.update({f"{name}+temperature": cov.quantiles(name) for name in cov.models()})
        y = plain.targets()
        first = pd.Timestamp(m.loc[idx[0], "cutoff"])
        hist = grid.loc[(grid.index >= first - pd.Timedelta(days=7)) & (grid.index < first), "ND"]
        cutoffs = []
        for i in idx:
            cut = pd.Timestamp(m.loc[i, "cutoff"])
            dates = pd.date_range(cut, periods=48, freq="30min")
            cutoffs.append({
                "cutoff": cut.isoformat(), "leak_free": leak, "t": [d.isoformat() for d in dates],
                "actual": [None if not np.isfinite(v) else int(v) for v in y[i]],
                "forecasts": {name: {f"q{k}": [int(round(v)) for v in q[i, :, j]] for k, j in (("10", 0), ("50", 4), ("90", 8))}
                              for name, q in qs.items()},
            })
        series.append({
            "id": sid, "label": lab, "kind": "grid", "freq": "30min", "note": note,
            "history": {"t": [d.isoformat() for d in hist.index], "y": [None if not np.isfinite(v) else int(v) for v in hist]},
            "cutoffs": cutoffs,
        })
    model_ids = sorted({k for s in series for c in s["cutoffs"] for k in c["forecasts"]})
    payload = {
        "generated": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
        "machine": summary.machine,
        "models": [{"id": mid, "label": label(mid)} for mid in model_ids],
        "series": series,
        "sweep": {
            "lengths_weeks": lengths,
            "n_series": sweep["n_series"],
            "n_windows": sweep["n_windows"],
            "relmase": {mm: [sig(sweep["relmase"][mm].get(n)) for n in lengths] for mm in sweep["relmase"]},
            "relwql": {mm: [sig(sweep["relwql"][mm].get(n)) for n in lengths] for mm in sweep["relwql"]},
        },
    }
    out.write_text(json.dumps(payload, separators=(",", ":")))


def pick_products(forecasts: Path, products: pd.DataFrame, cutoffs: list[str]) -> list[dict]:
    """~12 retail products spanning the story, chosen by rule from the scored sample."""
    meta = Task(forecasts / "retail").windows()
    weekly = pd.read_parquet("data/prepared/retail_weekly.parquet")
    stats = []
    for code, g in weekly[weekly["unique_id"].isin(meta["series"].unique())].groupby("unique_id"):
        y = g["y"].to_numpy()
        ds = pd.DatetimeIndex(g["ds"])
        before = ds <= pd.Timestamp(cutoffs[0])
        peak = (ds >= "2010-11-01") & (ds <= "2010-12-31")
        stats.append({
            "code": code, "mean": y.mean(), "zeros": float(np.mean(y[before] == 0)) if before.any() else 1.0,
            "start": ds.min(), "xmas_share": y[peak].sum() / max(y[(ds >= "2010-01-01") & (ds <= "2010-12-31")].sum(), 1),
            "windows": int((meta["series"] == code).sum()),
        })
    st = pd.DataFrame(stats)
    full = st[st["windows"] == 5]
    chosen: list[dict] = []

    def take(frame: pd.DataFrame, role: str, note: str, k: int) -> None:
        for code in frame["code"]:
            if len([c for c in chosen if c["role"] == role]) >= k:
                break
            if code in {c["code"] for c in chosen}:
                continue
            m = meta[meta["series"] == code]
            available = [c[:10] for c in m["cutoff"]]
            use = [c for c in cutoffs if c in available][-3:]
            chosen.append({"code": code, "role": role, "note": note, "cutoffs": use})

    take(full.sort_values("mean", ascending=False), "best-seller", "Dense, high-volume product with two years of history", 2)
    take(st.sort_values("start", ascending=False), "new product", "Launched shortly before the cut-offs: little history", 2)
    take(full[full["mean"] > 3].sort_values("zeros", ascending=False), "intermittent", "Most weeks sell nothing", 2)
    on_sale_all_2010 = full[(full["mean"] > 5) & (full["start"] <= pd.Timestamp("2010-01-31"))]
    take(on_sale_all_2010.sort_values("xmas_share", ascending=False), "Nov-Dec seller",
         "On sale all of 2010, yet most of that year's sales came in November and December", 2)
    take(full.sample(frac=1.0, random_state=7), "typical", "A randomly drawn product from the sample", 4)
    return chosen


FLOOR_GRID_MODELS = [
    ("seasonal-naive", ""), ("ets-aaa", ""), ("lightgbm-context-only", "_temp"), ("theory-context", "_temp"),
    ("theory-prior-2024", "_temp"), ("timestral-5m", "_temp"), ("timestral-209m", "_temp"), ("chronos-2", "_temp"),
    ("timesfm-2.5", ""), ("timesfm-3", "_temp"), ("t0-gamma", "_temp"),
]
FLOOR_COLOURS = {**LINES, "theory-context": "#1baf7a", "theory-prior-2024": "#008300", "t0-gamma": "#4a3aa7",
                 "lightgbm-context-only": "#e87ba4", "lightgbm-transfer": "#e34948", "lightgbm": "#e87ba4",
                 "chronos-2": "#9085e9"}


def floor_curves(summary: Summary, tasks: list[tuple[int, str]], models: list[tuple[str, str]]) -> dict:
    """{model: {length: row}} for (length, task name) pairs; suffix picks the covariate task."""
    curves: dict = {}
    for n, name in tasks:
        for model, suffix in models:
            t = summary.table(name + suffix)
            if t.empty or model not in set(t["model"]):
                continue
            row = t[t["model"] == model].iloc[0]
            curves.setdefault(model + ("+temperature" if suffix else ""), {})[n] = row
    return curves


def floor_chart(curves: dict, lengths: list[int], ticks: list[str], unit: str, title: str, footnote: str,
                path: Path, highlight: str, mase_key: str = "relative_mase_geomean",
                mase_label: str = "MASE relative to seasonal naive") -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    for ax, key, ylabel in zip(axes, [mase_key, "relative_wql_pooled"],
                               [mase_label, "WQL relative to seasonal naive"]):
        style(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        for model, points in curves.items():
            base = model.split("+")[0]
            xs = [n for n in lengths if n in points]
            ys = [float(points[n][key]) for n in xs]
            dashed = family(base) == "fitted"
            width = 3 if model == highlight else 1.6
            ax.plot(xs, ys, color=FLOOR_COLOURS.get(base, INK), linewidth=width, marker="o", markersize=4,
                    linestyle="--" if dashed else "-", label=label(model))
            if model == highlight and key == "relative_mase_geomean":
                lo = [points[n]["relative_mase_ci95"][0] for n in xs]
                hi = [points[n]["relative_mase_ci95"][1] for n in xs]
                ax.fill_between(xs, lo, hi, color=FLOOR_COLOURS.get(base, INK), alpha=0.15, linewidth=0)
        ax.axhline(1.0, color=MUTED, linewidth=0.8, linestyle=":")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(lengths)
        ax.set_xticklabels(ticks, fontsize=8)
        ax.set_yticks([0.3, 0.5, 0.7, 1, 2, 3, 5])
        ax.set_yticklabels(["0.3", "0.5", "0.7", "1", "2", "3", "5"], fontsize=8)
        ax.minorticks_off()
        ax.set_xlabel(f"History given to every model ({unit})", fontsize=8, color=MUTED)
        ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
    axes[0].set_title(title, loc="left", fontsize=10, color=INK)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.04))
    fig.text(0.01, 0.005, footnote, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.23, 1, 1))
    save(fig, path)


EXTRAP_MODELS = [("seasonal-naive", ""), ("ets-aaa", ""), ("lightgbm-no-lags", "_temp"), ("theory-context", "_temp"),
                 ("theory-prior-2024", "_temp"), ("timestral-209m", "_temp"), ("chronos-2", "_temp"),
                 ("timesfm-3", "_temp"), ("t0-gamma", "_temp")]


def extrapolation_daily(forecasts: Path) -> tuple[pd.DataFrame, dict]:
    """Daily (UK local day) means of the actual series and of each model's quantiles, Sep-Nov 2025."""
    grid = pd.read_parquet("data/prepared/grid_halfhourly.parquet").set_index("ds")
    plain = Task(forecasts / "extrap_long")
    temp = Task(forecasts / "extrap_long_temp")
    meta = plain.windows()
    cut = pd.Timestamp(meta["cutoff"].iloc[0])
    horizon = plain.targets().shape[1]
    dates = pd.date_range(cut, periods=horizon, freq="30min")
    day = dates.tz_convert("Europe/London").tz_localize(None).normalize()
    actual = grid["ND"].reindex(dates).to_numpy()
    frame = pd.DataFrame({"day": day, "actual": actual, "temperature": grid["temperature"].reindex(dates).to_numpy()})
    models = {}
    for model, suffix in EXTRAP_MODELS:
        task = temp if suffix else plain
        if model not in task.models():
            continue
        q = task.quantiles(model)[0]
        name = model + ("+temperature" if suffix else "")
        models[name] = pd.DataFrame({"day": day, "q10": q[:, 0], "q50": q[:, 4], "q90": q[:, 8]}).groupby("day").mean()
    return frame.groupby("day").mean(), models


def extrapolation_chart(forecasts: Path, path: Path) -> None:
    daily, models = extrapolation_daily(forecasts)
    fig, (ax, axt) = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    style(ax)
    style(axt)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    scored = daily.index >= pd.Timestamp("2025-10-01")
    ax.axvspan(daily.index[scored][0], daily.index[-1], color="#f3f2ee", zorder=0)
    ax.text(daily.index[scored][0], daily["actual"].max(), "  scored: 1 Oct-30 Nov", fontsize=8, color=MUTED, va="top")
    ax.plot(daily.index, daily["actual"], color=INK, linewidth=2.6, label="Actual")
    for name, d in models.items():
        base = name.split("+")[0]
        ax.plot(d.index, d["q50"], color=FLOOR_COLOURS.get(base, INK), linewidth=1.6,
                linestyle="--" if family(base) == "fitted" else "-", label=label(name))
    ax.set_ylabel("Daily mean national demand (MW)", fontsize=8, color=MUTED)
    ax.set_title("Forecast from summer only (context 1 Jun-31 Aug 2025), one run to 30 Nov; median, daily means",
                 loc="left", fontsize=10, color=INK)
    axt.plot(daily.index, daily["temperature"], color=MUTED, linewidth=1.5)
    axt.set_ylabel("GB mean temp. (C)", fontsize=8, color=MUTED)
    axt.grid(axis="y", color=GRID, linewidth=0.8)
    handles, names = ax.get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, path)


def demo_id(model: str) -> str:
    """Theory models always take temperature, so their demo ids drop the suffix."""
    return model.replace("+temperature", "") if model.startswith("theory") else model


def extend_demo(path: Path, summary: Summary, forecasts: Path, grid_lengths: list[int], retail_lengths: list[int]) -> None:
    payload = json.loads(path.read_text())
    grid = floor_curves(summary, [(n, f"grid_floor_L{n:04d}") for n in grid_lengths],
                        [(m, "") for m in ["seasonal-naive", "ets-aaa", "lightgbm-context-only", "timestral-5m",
                                           "timestral-209m", "chronos-2", "timesfm-2.5", "timesfm-3", "t0-gamma",
                                           "t0-beta"]]
                        + [(m, "_temp") for m in ["lightgbm-context-only", "theory-context", "theory-prior-2024",
                                                 "timestral-5m", "timestral-209m", "chronos-2", "timesfm-3",
                                                 "t0-gamma", "t0-beta"]])
    retail = floor_curves(summary, [(n, f"retail_floor_L{n:02d}") for n in retail_lengths],
                          [(m, "") for m in ["seasonal-naive", "autoets", "lightgbm-transfer", "timestral-5m",
                                             "timestral-209m", "chronos-2", "timesfm-2.5", "timesfm-3", "t0-gamma",
                                             "t0-beta"]])

    def block(curves, lengths, key):
        return {demo_id(m): [sig(float(p[n][key])) if n in p else None for n in lengths] for m, p in curves.items()}

    first = lambda curves: next(iter(next(iter(curves.values())).values()))  # noqa: E731
    payload["sweep_grid"] = {
        "lengths_halfhours": grid_lengths, "n_windows": int(first(grid)["windows"]),
        "relmase": block(grid, grid_lengths, "relative_mase_geomean"),
        "relwql": block(grid, grid_lengths, "relative_wql_pooled"),
        "note": "baseline = seasonal naive (same half-hour last week) with 7 days; null = cannot fit",
    }
    payload["sweep_retail_floor"] = {
        "lengths_weeks": retail_lengths, "n_series": int(first(retail)["series"]),
        "n_windows": int(first(retail)["windows"]),
        "relmase": block(retail, retail_lengths, "relative_mase_geomean"),
        "relwql": block(retail, retail_lengths, "relative_wql_pooled"),
        "note": "same products, targets and baseline as sweep; null = cannot fit",
    }
    daily, models = extrapolation_daily(forecasts)
    g = pd.read_parquet("data/prepared/grid_halfhourly.parquet").set_index("ds")
    start = pd.Timestamp("2025-06-01", tz="Europe/London").tz_convert("UTC")
    cut = pd.Timestamp("2025-09-01", tz="Europe/London").tz_convert("UTC")
    summer = g.loc[(g.index >= start) & (g.index < cut), "ND"]
    hist = summer.groupby(summer.index.tz_convert("Europe/London").tz_localize(None).normalize()).mean()
    series = [x for x in payload["series"] if x["id"] != "grid-extrapolation"]
    series.append({
        "id": "grid-extrapolation", "label": "GB national demand: summer history, autumn forecast",
        "kind": "grid", "freq": "D",
        "note": "Daily means. Every model saw only 1 Jun-31 Aug 2025 and forecast to 30 Nov in one run; "
                "scored on 1 Oct-30 Nov. Temperature (measured, an oracle) given to models that take it.",
        "history": {"t": [d.date().isoformat() for d in hist.index], "y": [int(round(v)) for v in hist]},
        "cutoffs": [{
            "cutoff": "2025-09-01", "leak_free": False, "t": [d.date().isoformat() for d in daily.index],
            "actual": [int(round(v)) for v in daily["actual"]],
            "forecasts": {demo_id(m): {k: [int(round(v)) for v in d[c]] for k, c in (("q10", "q10"), ("q50", "q50"), ("q90", "q90"))}
                          for m, d in models.items()},
        }],
    })
    payload["series"] = series
    known = {m["id"] for m in payload["models"]}
    for m in list(models) + list(grid) + list(retail):
        if demo_id(m) not in known:
            payload["models"].append({"id": demo_id(m), "label": label(demo_id(m))})
            known.add(demo_id(m))
    path.write_text(json.dumps(payload, separators=(",", ":")))
