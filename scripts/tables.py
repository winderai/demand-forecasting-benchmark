"""Render the Markdown tables in results/tables.md from results/summary.json (pasted into the README)."""

import json
from pathlib import Path

import pandas as pd

from forecastbench.report import label

TASKS = [
    ("retail", None, "Retail (UCI Online Retail II), 8 weeks ahead"),
    ("retail_calendar", None, "Retail, Timestral with calendar covariates"),
    ("grid_historic", "grid_historic_temp", "GB national demand, 28 days of 2025, day ahead"),
    ("grid_leakfree", "grid_leakfree_temp", "GB national demand, leak-free window (targets 15-19 Oct 2026), day ahead"),
    ("fresh", "fresh_promo", "FreshRetailNet-50K, 7 days ahead, with and without the planned discount"),
]
SWEEPS = [("retail_sweep_L", [8, 13, 26, 52, 78], "{:02d}", "weeks"), ("grid_sweep_L", [48, 336, 1344, 4032], "{:04d}", "half-hours")]


def fmt(x, digits=3):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "n/a"
    return f"{x:.{digits}f}"


def table(rows: pd.DataFrame, retail: bool) -> str:
    head = "| Model | Windows | Series | Rel. MASE (95% CI) | Rel. WQL | MASE | WQL | 10-90% coverage | s per window |"
    if retail:
        head += " Units short @p90 | Units over @p90 |"
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for _, r in rows.iterrows():
        ci = r["relative_mase_ci95"]
        cells = [label(r["model"]), str(r["windows"]), str(r["series"]),
                 f"{fmt(r['relative_mase_geomean'])} ({fmt(ci[0], 2)}-{fmt(ci[1], 2)})",
                 fmt(r["relative_wql_pooled"]), fmt(r["mase_mean"]), fmt(r["wql_pooled"]),
                 fmt(r["coverage_10_90"], 2), fmt(r["s_per_window"], 4)]
        if retail:
            cells += [fmt(r["units_short_at_p90"], 0), fmt(r["units_excess_at_p90"], 0)]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


FLOORS = [
    ("grid_floor_L", [12, 24, 48, 96, 144, 336], "{:04d}", "_temp", "half-hours",
     "GB demand floor sweep: 28 day-ahead forecasts across 2025, same targets at every length"),
    ("retail_floor_L", [1, 2, 4, 8], "{:02d}", None, "weeks",
     "Retail floor sweep, the 80 sweep products (342 windows)"),
    ("retail300_floor_L", [1, 2, 4, 8], "{:02d}", None, "weeks",
     "Retail floor sweep, the 300-product sample (1,332 windows)"),
]
EXTRAPOLATION = [("extrap_long", "Out of range: summer context (1 Jun-31 Aug 2025), one forecast to 30 Nov, "
                  "scored on 1 Oct-30 Nov (2,930 half-hours)"),
                 ("extrap_dayahead", "Out of range, day ahead: the same summer context frozen, a gap of missing "
                  "values to each forecast day, 61 day-ahead forecasts for 1 Oct-30 Nov")]


def floor_tables(s: dict) -> list[str]:
    out = []
    for prefix, lengths, pattern, cov, unit, title in FLOORS:
        rows = {}
        failures = {}
        for n in lengths:
            for suffix, tag in [("", "")] + ([(cov, "+temperature")] if cov else []):
                name = prefix + pattern.format(n) + suffix
                task = s["tasks"].get(name)
                if task is None:
                    continue
                for r in task["rows"]:
                    rows.setdefault(r["model"] + tag, {})[n] = r
                for model, f in task.get("failures", {}).items():
                    failures.setdefault(model + tag, {})[n] = f["error"].splitlines()[0]
        if not rows:
            continue
        n_windows = next(iter(next(iter(rows.values())).values()))["windows"]
        head = "| Model | " + " | ".join(f"{x} {unit}" for x in lengths) + " |"
        sep = "|" + "---|" * (len(lengths) + 1)
        blocks = [
            ("Relative MASE (95% CI), baseline = seasonal naive with the longest history",
             lambda r: f"{fmt(r['relative_mase_geomean'])} ({fmt(r['relative_mase_ci95'][0], 2)}-{fmt(r['relative_mase_ci95'][1], 2)})"),
            ("Mean MASE over the baseline's mean MASE (an arithmetic check on the geometric mean)",
             lambda r: fmt(r.get("relative_mase_of_means"))),
            ("Relative MASE against the seasonal naive at the same length",
             lambda r: fmt(r.get("relative_mase_vs_same_length_naive"))),
            ("Relative WQL (pooled)", lambda r: fmt(r["relative_wql_pooled"])),
            ("10-90% coverage", lambda r: fmt(r["coverage_10_90"], 2)),
        ]
        out.append(f"### {title} (N = {n_windows} windows per length)\n")
        for caption, cell in blocks:
            lines = [f"{caption}:\n", head, sep]
            for m in sorted(set(rows) | set(failures)):
                cells = []
                for x in lengths:
                    if x in rows.get(m, {}):
                        cells.append(cell(rows[m][x]))
                    elif x in failures.get(m, {}):
                        cells.append("cannot fit")
                    else:
                        cells.append("n/a")
                lines.append(f"| {label(m)} | " + " | ".join(cells) + " |")
            out.append("\n".join(lines) + "\n")
    pairs = s.get("floor_pairs", [])
    if pairs:
        lines = ["### Head to head on the same windows (geometric mean of MASE ratios, 95% CI; below 1 = first model better)\n",
                 "| Task | Model | Against | Ratio (95% CI) | Ratio of mean MASE |", "|---|---|---|---|---|"]
        for p in pairs:
            ratio = "cannot fit" if p["ratio"] is None else f"{fmt(p['ratio'])} ({fmt(p['ci95'][0], 2)}-{fmt(p['ci95'][1], 2)})"
            means = "" if p["ratio"] is None else fmt(p.get("ratio_of_mean_mase"))
            lines.append(f"| {p['task']} | {label(p['model'])} | {label(p['rival'])} | {ratio} | {means} |")
        out.append("\n".join(lines) + "\n")
    for name, title in EXTRAPOLATION:
        if name not in s["tasks"]:
            continue
        rows = pd.DataFrame(s["tasks"][name]["rows"])
        if name + "_temp" in s["tasks"]:
            extra = pd.DataFrame(s["tasks"][name + "_temp"]["rows"])
            extra["model"] = extra["model"] + "+temperature"
            rows = pd.concat([rows, extra])
        rows = rows.sort_values("relative_mase_geomean")
        out.append(f"### {title}\n\n{table(rows, False)}\n")
    return out


def main() -> None:
    s = json.loads(Path("results/summary.json").read_text())
    out = []
    for plain, cov, title in TASKS:
        if plain not in s["tasks"]:
            continue
        rows = pd.DataFrame(s["tasks"][plain]["rows"])
        if cov and cov in s["tasks"]:
            extra = pd.DataFrame(s["tasks"][cov]["rows"])
            extra["model"] = extra["model"] + ("+temperature" if cov.startswith("grid") else "+promo")
            rows = pd.concat([rows, extra])
        rows = rows.sort_values("relative_mase_geomean")
        out.append(f"### {title}\n\n{table(rows, plain in ('retail', 'retail_calendar', 'fresh'))}\n")
        failures = {**s["tasks"][plain].get("failures", {}), **(s["tasks"].get(cov, {}).get("failures", {}) if cov else {})}
        if failures:
            out.append("Failures: " + "; ".join(f"{k}: {v['error'].splitlines()[0]}" for k, v in failures.items()) + "\n")
    for prefix, lengths, pattern, unit in SWEEPS:
        models = {}
        n = None
        for length in lengths:
            name = prefix + pattern.format(length)
            if name not in s["tasks"]:
                continue
            for r in s["tasks"][name]["rows"]:
                models.setdefault(r["model"], {})[length] = (r["relative_mase_geomean"], r["relative_wql_pooled"], r["mase_mean"])
                n = (r["windows"], r["series"])
        if not models:
            continue
        head = "| Model | " + " | ".join(f"L={x}" for x in lengths) + " |"
        lines = [f"### History-length sweep ({prefix[:-2]}, {unit}; {n[0]} windows, {n[1]} series)\n",
                 "Relative MASE (geometric mean) / relative WQL (pooled) / mean MASE; seasonal naive with the "
                 "longest history = 1 for the two relative figures:\n", head,
                 "|" + "---|" * (len(lengths) + 1)]
        for m, v in sorted(models.items()):
            lines.append(f"| {label(m)} | " + " | ".join(
                f"{fmt(v[x][0])} / {fmt(v[x][1])} / {fmt(v[x][2])}" if x in v else "n/a" for x in lengths) + " |")
        out.append("\n".join(lines) + "\n")
    out += floor_tables(s)
    Path("results/tables.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
