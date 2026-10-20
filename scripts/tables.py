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
        lines = [f"### History-length sweep ({prefix[:-3]}, {unit}; {n[0]} windows, {n[1]} series)\n",
                 "Relative MASE / relative WQL (seasonal naive with the longest history = 1):\n", head,
                 "|" + "---|" * (len(lengths) + 1)]
        for m, v in sorted(models.items()):
            lines.append(f"| {label(m)} | " + " | ".join(
                f"{fmt(v[x][0])} / {fmt(v[x][1])}" if x in v else "n/a" for x in lengths) + " |")
        out.append("\n".join(lines) + "\n")
    Path("results/tables.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
