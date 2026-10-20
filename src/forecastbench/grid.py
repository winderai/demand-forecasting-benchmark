"""NESO GB national demand (ND), half-hourly, with BMRS daily average temperature."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

LONDON = "Europe/London"


class Settlements:
    """NESO demand files: settlement date and period, converted to a UTC half-hour index."""

    def __init__(self, files: list[Path]):
        self._files = files

    def frame(self) -> pd.DataFrame:
        parts = []
        for f in self._files:
            d = pd.read_csv(f)
            if "FORECAST_ACTUAL_INDICATOR" in d.columns:
                d = d[d["FORECAST_ACTUAL_INDICATOR"] == "A"]
            d["day"] = pd.to_datetime(d["SETTLEMENT_DATE"], format="mixed").dt.normalize()
            parts.append(d[["day", "SETTLEMENT_PERIOD", "ND", "TSD"]])
        d = pd.concat(parts).drop_duplicates(["day", "SETTLEMENT_PERIOD"], keep="last")
        midnight = d["day"].dt.tz_localize(LONDON).dt.tz_convert("UTC")
        d["ds"] = midnight + pd.to_timedelta((d["SETTLEMENT_PERIOD"] - 1) * 30, unit="min")
        d = d.sort_values("ds").drop_duplicates("ds", keep="last")
        return d[["ds", "day", "ND", "TSD"]]


class Temperatures:
    """BMRS TEMP: GB daily average temperature outturn (published the same afternoon)."""

    def __init__(self, files: list[Path]):
        self._files = files

    def series(self) -> pd.Series:
        rows = []
        for f in self._files:
            rows += json.loads(f.read_text())["data"]
        d = pd.DataFrame(rows)
        d["day"] = pd.to_datetime(d["measurementDate"])
        d = d.sort_values("publishTime").drop_duplicates("day", keep="last")
        return d.set_index("day")["temperature"].sort_index()


def prepare(raw: Path, out: Path, notes: Path) -> None:
    demand = Settlements(
        sorted(raw.glob("neso_demanddata_20*.csv")) + [raw / "neso_demanddataupdate.csv"]
    ).frame()
    temps = Temperatures(sorted(raw.glob("bmrs_temp_*.json"))).series()
    start, end = demand["ds"].min(), demand["ds"].max()
    index = pd.date_range(start, end, freq="30min", tz="UTC")
    frame = demand.set_index("ds").reindex(index)
    frame.index.name = "ds"
    local_day = index.tz_convert(LONDON).tz_localize(None).normalize()
    full_days = pd.date_range(temps.index.min(), max(temps.index.max(), local_day.max()), freq="D")
    daily = temps.reindex(full_days).ffill()
    frame["temperature"] = daily.reindex(local_day).to_numpy()
    frame = frame.reset_index()[["ds", "ND", "TSD", "temperature"]]
    frame.to_parquet(out, index=False)
    missing = frame[frame["ND"].isna()]
    info = {
        "target": "ND (national demand, MW): transmission demand excluding station load, pumping and exports",
        "first_ds_utc": str(start),
        "last_ds_utc": str(end),
        "rows": int(len(frame)),
        "missing_nd_half_hours": [str(x) for x in missing["ds"]],
        "temperature_days_missing_filled_forward": [
            str(x.date()) for x in full_days if x not in temps.index
        ],
        "temperature_last_published_day": str(temps.index.max().date()),
        "temperature_note": "Daily GB average temperature outturn (BMRS TEMP), repeated over the 48 half-hours "
        "of its local day. It is an actual, not a forecast: an oracle covariate.",
        "neso_note": "NESO notes data issues on its Demand Data Update for 2026-10-03 to 2026-10-13 "
        "(under review on 2026-10-20); those days are used as published.",
        "nd_mean_mw": float(np.nanmean(frame["ND"])),
    }
    notes.write_text(json.dumps(info, indent=2))
