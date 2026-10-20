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
}
FITTED = {"autoets", "croston", "tsb", "lightgbm", "lightgbm-context-only"}
BASELINES = {"seasonal-naive"}
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
COLOURS = {"baseline": "#8a8984", "fitted": "#eb6834", "pretrained": "#2a78d6"}
LINES = {
    "seasonal-naive": "#8a8984", "autoets": "#eb6834", "lightgbm": "#4a3aa7", "lightgbm-context-only": "#4a3aa7",
    "timestral-209m": "#2a78d6", "timestral-5m": "#1baf7a", "chronos-2": "#e87ba4", "t0-gamma": "#008300",
    "timesfm-3": "#eda100", "timesfm-2.5": "#e34948",
}
SWEEP_MODELS = ["seasonal-naive", "autoets", "lightgbm", "lightgbm-context-only", "timestral-5m", "timestral-209m",
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
            for yi, v in zip(y, values):
                if np.isfinite(v):
                    ax.text(v, yi, f" {v:.2f}", va="center", fontsize=7, color=INK)
            ax.axvline(1.0, color=MUTED, linewidth=0.8, linestyle="--")
            ax.set_yticks(y)
            ax.set_yticklabels([label(m) for m in t["model"]] if c == 0 else [], fontsize=8, color=INK)
            ax.set_xlabel(xlabel, fontsize=8, color=MUTED)
            if c == 0:
                ax.set_title(title, loc="left", fontsize=10, color=INK)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOURS[k]) for k in ("baseline", "fitted", "pretrained")]
    fig.legend(handles, ["Baseline", "Fitted per cut-off", "Pretrained (zero-shot)"], loc="lower center", ncol=3,
               frameon=False, fontsize=8)
    fig.text(0.01, 0.005, "Lower is better. Geometric mean over windows; bars on MASE are 95% series-bootstrap "
             "intervals. " + summary.machine + ", CPU.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
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


def sweep_chart(curves: dict, lengths: list[int], unit: str, title: str, path: Path, ticks: list[str]) -> None:
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
            ax.text(xs[-1], ys[-1], "  " + label(model).split(" (")[0], fontsize=7, color=INK, va="center")
        ax.set_xscale("log")
        ax.set_xticks(lengths)
        ax.set_xticklabels(ticks, fontsize=8)
        ax.minorticks_off()
        ax.set_xlabel(f"History given to every model ({unit})", fontsize=8, color=MUTED)
        ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
    axes[0].set_title(title, loc="left", fontsize=10, color=INK)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
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
    take(full[full["mean"] > 5].sort_values("xmas_share", ascending=False), "Christmas item", "Most of 2010's sales came in November and December", 2)
    take(full.sample(frac=1.0, random_state=7), "typical", "A randomly drawn product from the sample", 4)
    return chosen
