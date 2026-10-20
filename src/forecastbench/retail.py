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
        d = d[~cancelled]
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
