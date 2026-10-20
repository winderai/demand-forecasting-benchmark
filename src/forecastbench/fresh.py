"""FreshRetailNet-50K: daily store-product sales with a planned discount, the promotion test."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from forecastbench.windows import Windows

COLUMNS = ["store_id", "product_id", "dt", "sale_amount", "discount", "holiday_flag", "activity_flag",
           "stock_hour6_22_cnt"]
KNOWN = ["discount", "holiday_flag", "activity_flag"]


class FreshRetail:
    """90 training days and a 7-day evaluation week per store-product series."""

    def __init__(self, train: Path, evaluation: Path):
        self._train = train
        self._eval = evaluation

    def frame(self) -> pd.DataFrame:
        t = pd.read_parquet(self._train, columns=COLUMNS).assign(split="train")
        e = pd.read_parquet(self._eval, columns=COLUMNS).assign(split="eval")
        d = pd.concat([t, e], ignore_index=True)
        d["unique_id"] = d["store_id"].astype(str) + "-" + d["product_id"].astype(str)
        d["ds"] = pd.to_datetime(d["dt"])
        return d.sort_values(["unique_id", "ds"]).reset_index(drop=True)

    def windows(self, name: str, sample: int, seed: int) -> tuple[Windows, dict]:
        d = self.frame()
        week = d[d["split"] == "eval"]
        varying = week.groupby("unique_id")["discount"].std()
        candidates = np.sort(varying[varying > 0].index.to_numpy())
        rng = np.random.default_rng(seed)
        chosen = np.sort(rng.choice(candidates, size=sample, replace=False))
        ids, cutoffs, contexts, targets, tdates, cdates, known = [], [], [], [], [], [], []
        stockout_days = 0
        for code, g in d[d["unique_id"].isin(chosen)].groupby("unique_id", sort=True):
            train = g[g["split"] == "train"]
            ev = g[g["split"] == "eval"]
            ids.append(code)
            cutoffs.append(pd.Timestamp(train["ds"].iloc[-1]))
            contexts.append(train["sale_amount"].to_numpy(dtype=float))
            targets.append(ev["sale_amount"].to_numpy(dtype=float))
            tdates.append(pd.DatetimeIndex(ev["ds"]))
            cdates.append(pd.DatetimeIndex(train["ds"]))
            known.append(g[KNOWN].to_numpy(dtype=float).T)
            stockout_days += int((ev["stock_hour6_22_cnt"] > 0).sum())
        notes = {
            "series_total": int(d["unique_id"].nunique()),
            "series_with_varying_discount_in_eval_week": int(len(candidates)),
            "sampled": sample,
            "seed": seed,
            "eval_days_with_a_stockout_hour": stockout_days,
            "eval_days": int(sample * 7),
            "note": "sale_amount is globally rescaled by the publisher; sales on stock-out days are censored demand",
        }
        return Windows(name, "D", 7, 1, ids, cutoffs, contexts, np.array(targets), tdates, list(contexts),
                       known, KNOWN, cdates), notes
