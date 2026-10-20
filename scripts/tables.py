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


def ci(pair) -> str:
    return f"({fmt(pair[0], 2)}-{fmt(pair[1], 2)})"


def table(rows: pd.DataFrame, retail: bool) -> str:
    """Retail-type tables lead with the ratio of mean MASE; dense grid tables with the geometric mean."""
    if retail:
        head = ("| Model | Windows | Series | Mean-MASE ratio (95% CI) | Geo. rel. MASE (95% CI) | Rel. WQL | MASE | WQL "
                "| 10-90% coverage | s per window | Units short @p90 | Units over @p90 |")
    else:
        head = ("| Model | Windows | Series | Geo. rel. MASE (95% CI) | Mean-MASE ratio (95% CI) | Rel. WQL | MASE | WQL "
                "| 10-90% coverage | s per window |")
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for _, r in rows.iterrows():
        geo = f"{fmt(r['relative_mase_geomean'])} {ci(r['relative_mase_ci95'])}"
        mean = f"{fmt(r['relative_mase_of_means'])} {ci(r['relative_mase_of_means_ci95'])}"
        first = [mean, geo] if retail else [geo, mean]
        cells = [label(r["model"]), str(r["windows"]), str(r["series"]), *first,
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
        mean_block = ("Mean-MASE ratio (95% CI), baseline = seasonal naive with the longest history",
                      lambda r: f"{fmt(r['relative_mase_of_means'])} {ci(r['relative_mase_of_means_ci95'])}")
        blocks = [
            ("Geometric-mean relative MASE (95% CI), baseline = seasonal naive with the longest history",
             lambda r: f"{fmt(r['relative_mase_geomean'])} ({fmt(r['relative_mase_ci95'][0], 2)}-{fmt(r['relative_mase_ci95'][1], 2)})"),
            ("Relative MASE against the seasonal naive at the same length",
             lambda r: fmt(r.get("relative_mase_vs_same_length_naive"))),
            ("Relative WQL (pooled)", lambda r: fmt(r["relative_wql_pooled"])),
            ("10-90% coverage", lambda r: fmt(r["coverage_10_90"], 2)),
        ]
        blocks = [mean_block] + blocks if prefix.startswith("retail") else blocks[:1] + [mean_block] + blocks[1:]
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
    pairs = s.get("head_to_head", [])
    if pairs:
        lines = ["### Head to head on the same windows (below 1 = first model better; 95% CIs resample whole series)\n",
                 "| Task | Model | Against | Ratio of mean MASE (95% CI) | Geometric mean of MASE ratios (95% CI) |",
                 "|---|---|---|---|---|"]
        for p in pairs:
            if p["ratio_of_mean_mase"] is None:
                lines.append(f"| {p['task']} | {label(p['model'])} | {label(p['rival'])} | cannot fit | cannot fit |")
                continue
            lines.append(f"| {p['task']} | {label(p['model'])} | {label(p['rival'])} | "
                         f"{fmt(p['ratio_of_mean_mase'])} {ci(p['ratio_of_mean_mase_ci95'])} | {fmt(p['ratio'])} {ci(p['ci95'])} |")
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
        retail = plain in ("retail", "retail_calendar", "fresh")
        rows = rows.sort_values("relative_mase_of_means" if retail else "relative_mase_geomean")
        out.append(f"### {title}\n\n{table(rows, retail)}\n")
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
                first = r["relative_mase_of_means"] if prefix.startswith("retail") else r["relative_mase_geomean"]
                second = r["relative_mase_geomean"] if prefix.startswith("retail") else r["relative_mase_of_means"]
                models.setdefault(r["model"], {})[length] = (first, r["relative_wql_pooled"], second)
                n = (r["windows"], r["series"])
        if not models:
            continue
        head = "| Model | " + " | ".join(f"L={x}" for x in lengths) + " |"
        lines = [f"### History-length sweep ({prefix[:-2]}, {unit}; {n[0]} windows, {n[1]} series)\n",
                 ("Mean-MASE ratio / relative WQL (pooled) / geometric-mean relative MASE" if prefix.startswith("retail")
                  else "Geometric-mean relative MASE / relative WQL (pooled) / mean-MASE ratio")
                 + "; seasonal naive with the longest history = 1:\n", head,
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
