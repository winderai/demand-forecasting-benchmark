"""UCI Online Retail II: clean the invoice lines and aggregate them to weekly units per product."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PRODUCT = r"^\d{5}[A-Z]{0,2}$"


class Invoices:
    """The raw invoice lines of the online gift retailer."""

    def __init__(self, workbook: Path, cache: Path):
        self._workbook = workbook
        self._cache = cache

    def lines(self) -> pd.DataFrame:
        if not self._cache.exists():
            sheets = pd.read_excel(
                self._workbook,
                sheet_name=None,
                dtype={"Invoice": str, "StockCode": str, "Description": str, "Country": str},
            )
            pd.concat(sheets.values(), ignore_index=True).to_parquet(self._cache)
        return pd.read_parquet(self._cache)


def cancelled_originals(lines: pd.DataFrame, cancelled: pd.Series) -> list[int]:
    """Index of each positive line that a later cancellation reverses exactly (same customer, code, quantity)."""
    keyed = lines.dropna(subset=["Customer ID"])
    positives = keyed[~cancelled.loc[keyed.index] & (keyed["Quantity"] > 0)]
    pool = {}
    for idx, row in positives.sort_values("InvoiceDate").iterrows():
        pool.setdefault((row["Customer ID"], row["StockCode"], row["Quantity"]), []).append((row["InvoiceDate"], idx))
    taken = []
    reversals = keyed[cancelled.loc[keyed.index] & (keyed["Quantity"] < 0)].sort_values("InvoiceDate")
    for _, row in reversals.iterrows():
        candidates = pool.get((row["Customer ID"], row["StockCode"], -row["Quantity"]), [])
        earlier = [c for c in candidates if c[0] <= row["InvoiceDate"]]
        if earlier:
            choice = earlier[-1]
            candidates.remove(choice)
            taken.append(choice[1])
    return taken


class WeeklySales:
    """Weekly units per StockCode (all countries), weeks ending Sunday, partial weeks dropped."""

    def __init__(self, invoices: Invoices):
        self._invoices = invoices

    def frame(self) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
        raw = self._invoices.lines()
        notes = {"raw_lines": int(len(raw))}
        d = raw.copy()
        d["Invoice"] = d["Invoice"].astype(str).str.strip()
        d["StockCode"] = d["StockCode"].astype(str).str.strip().str.upper()
        cancelled = d["Invoice"].str.startswith("C")
        notes["dropped_cancellations"] = int(cancelled.sum())
        matched = cancelled_originals(d, cancelled)
        notes["dropped_original_lines_matched_to_a_cancellation"] = int(len(matched))
        notes["dropped_original_units_matched_to_a_cancellation"] = int(d.loc[matched, "Quantity"].sum())
        notes["cancellation_matching"] = (
            "an original line is dropped when a later cancellation has the same customer, StockCode and "
            "quantity (the latest earlier match); this removes cancelled bulk orders such as 74,215 units "
            "of 23166 on 18 Jan 2011"
        )
        d = d[~cancelled & ~d.index.isin(matched)]
        bad = (d["Quantity"] <= 0) | (d["Price"] <= 0)
        notes["dropped_nonpositive_quantity_or_price"] = int(bad.sum())
        d = d[~bad]
        product = d["StockCode"].str.match(PRODUCT)
        notes["dropped_non_product_lines"] = int((~product).sum())
        notes["dropped_non_product_codes"] = sorted(d.loc[~product, "StockCode"].unique().tolist())
        d = d[product]
        d["ds"] = d["InvoiceDate"].dt.to_period("W-SUN").dt.end_time.dt.normalize()
        first_day, last_day = d["InvoiceDate"].min().normalize(), d["InvoiceDate"].max().normalize()
        weeks = d.groupby(["StockCode", "ds"], as_index=False)["Quantity"].sum()
        first_monday = first_day + pd.Timedelta(days=(7 - first_day.weekday()) % 7)
        first_full = first_monday + pd.Timedelta(days=6)
        last_full = last_day - pd.Timedelta(days=(last_day.weekday() + 1) % 7)
        notes["first_invoice"] = str(d["InvoiceDate"].min())
        notes["last_invoice"] = str(d["InvoiceDate"].max())
        notes["first_full_week_ending"] = str(first_full.date())
        notes["last_full_week_ending"] = str(last_full.date())
        weeks = weeks[(weeks["ds"] >= first_full) & (weeks["ds"] <= last_full)]
        calendar = pd.date_range(first_full, last_full, freq="W-SUN")
        notes["weeks"] = len(calendar)
        frames = []
        for code, g in weeks.groupby("StockCode"):
            span = calendar[calendar >= g["ds"].min()]
            s = g.set_index("ds")["Quantity"].reindex(span, fill_value=0)
            frames.append(pd.DataFrame({"unique_id": code, "ds": span, "y": s.to_numpy(dtype=float)}))
        out = pd.concat(frames, ignore_index=True)
        names = (
            d.dropna(subset=["Description"]).groupby("StockCode")["Description"]
            .agg(lambda x: x.str.strip().value_counts().index[0]).rename("description").reset_index()
        )
        notes["products"] = int(out["unique_id"].nunique())
        notes["description"] = (
            "Series start at each product's first week with a sale and are zero-filled to the last full week."
        )
        return out, notes, names


def prepare(workbook: Path, cache: Path, out: Path, notes: Path) -> None:
    frame, info, names = WeeklySales(Invoices(workbook, cache)).frame()
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out, index=False)
    notes.write_text(json.dumps(info, indent=2))
    names.to_parquet(out.parent / "retail_products.parquet", index=False)
