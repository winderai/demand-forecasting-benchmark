"""Public data sources: where each file comes from, and a manifest of what was fetched."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
from pathlib import Path

import requests


class Source:
    """One downloadable file with its provenance."""

    def __init__(self, name: str, url: str, licence: str, page: str, target: Path):
        self._name = name
        self._url = url
        self._licence = licence
        self._page = page
        self._target = target

    def fetch(self) -> dict:
        self._target.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(self._url, timeout=300)
        response.raise_for_status()
        self._target.write_bytes(response.content)
        return {
            "name": self._name,
            "url": self._url,
            "page": self._page,
            "licence": self._licence,
            "file": str(self._target),
            "bytes": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "downloaded_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }


NESO_LICENCE = "NESO Open Data Licence (https://www.neso.energy/data-portal/ngeso-open-licence)"
NESO_HISTORIC = "https://www.neso.energy/data-portal/historic-demand-data"
NESO_UPDATE = "https://www.neso.energy/data-portal/daily-demand-update"
NESO_BASE = "https://api.neso.energy/dataset"


def retail(raw: Path) -> list[Source]:
    return [
        Source(
            "UCI Online Retail II (id 502)",
            "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
            "Creative Commons Attribution 4.0 International (CC BY 4.0), as stated on the UCI page",
            "https://archive.ics.uci.edu/dataset/502/online+retail+ii",
            raw / "online_retail_ii.zip",
        )
    ]


def grid(raw: Path) -> list[Source]:
    years = {
        2024: "f6d02c0f-957b-48cb-82ee-09003f2ba759/download/demanddata_2024.csv",
        2025: "b2bde559-3455-4021-b179-dfe60c0337b0/download/demanddata_2025.csv",
        2026: "8a4a771c-3929-4e56-93ad-cdf13219dea5/download/demanddataupdate_2026.csv",
    }
    historic = "8f2fe0af-871c-488d-8bad-960426f24601/resource"
    files = [
        Source(
            f"NESO Historic Demand Data {year}",
            f"{NESO_BASE}/{historic}/{path}",
            NESO_LICENCE,
            NESO_HISTORIC,
            raw / f"neso_demanddata_{year}.csv",
        )
        for year, path in years.items()
    ]
    files.append(
        Source(
            "NESO Demand Data Update (daily, ~10 day settlement lag, latest actuals)",
            f"{NESO_BASE}/7a12172a-939c-404c-b581-a6128b74f588/resource/"
            "177f6fa4-ae49-4182-81ea-0c6b35f26ca6/download/demanddataupdate.csv",
            NESO_LICENCE,
            NESO_UPDATE,
            raw / "neso_demanddataupdate.csv",
        )
    )
    return files


BMRS_LICENCE = (
    "Elexon BMRS Data Licence; attribution required: 'Contains BMRS data (c) Elexon Limited copyright and "
    "database right 2026' (https://www.elexon.co.uk/bsc/data/balancing-mechanism-reporting-agent/"
    "copyright-licence-bmrs-data/)"
)


def temperature(raw: Path, years: list[tuple[str, str]]) -> list[Source]:
    """BMRS TEMP: GB daily average temperature (an outturn, so an oracle covariate)."""
    return [
        Source(
            f"Elexon BMRS TEMP {start} to {end}",
            f"https://data.elexon.co.uk/bmrs/api/v1/temperature?from={start}&to={end}&format=json",
            BMRS_LICENCE,
            "https://bmrs.elexon.co.uk/temperature",
            raw / f"bmrs_temp_{start}_{end}.json",
        )
        for start, end in years
    ]


def manifest(sources: list[Source], path: Path) -> None:
    entries = []
    for source in sources:
        entries.append(source.fetch())
        time.sleep(1.0)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(path.read_text()) if path.exists() else []
    keep = [e for e in existing if e["name"] not in {x["name"] for x in entries}]
    path.write_text(json.dumps(keep + entries, indent=2))


def fresh(raw: Path) -> list[Source]:
    base = "https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/resolve/main/data"
    return [
        Source(
            f"FreshRetailNet-50K {split}",
            f"{base}/{split}.parquet",
            "Creative Commons Attribution 4.0 International (CC BY 4.0), as stated on the dataset card",
            "https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K",
            raw / f"freshretailnet_{split}.parquet",
        )
        for split in ("train", "eval")
    ]
