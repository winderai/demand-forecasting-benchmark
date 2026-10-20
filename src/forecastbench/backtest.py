"""Run contenders over a window set and keep every forecast, with timings, on disk."""

from __future__ import annotations

import json
import os
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from forecastbench.metrics import scale
from forecastbench.windows import Windows


class Store:
    """results/forecasts/<task>/: windows.parquet, targets.npy, <model>.npz, timings.json, failures.json."""

    def __init__(self, root: Path, task: str):
        self._dir = root / task

    def keep_windows(self, windows: Windows) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        meta = pd.DataFrame({
            "key": windows.keys(),
            "series": windows.ids,
            "cutoff": [c.isoformat() for c in windows.cutoffs],
            "context_length": [len(c) for c in windows.contexts],
            "history_length": [len(h) for h in windows.history],
            "scale": [scale(h, windows.period) for h in windows.history],
            "first_target": [str(d[0]) for d in windows.target_dates],
        })
        meta.to_parquet(self._dir / "windows.parquet", index=False)
        np.save(self._dir / "targets.npy", windows.targets)

    def has(self, model: str) -> bool:
        return (self._dir / f"{model}.npz").exists()

    def keep(self, model: str, quantiles: np.ndarray, timing: dict) -> None:
        np.savez_compressed(self._dir / f"{model}.npz", quantiles=quantiles.astype(np.float32))
        self._merge("timings.json", model, timing)

    def fail(self, model: str, error: str) -> None:
        self._merge("failures.json", model, {"error": error})

    def _merge(self, file: str, model: str, entry: dict) -> None:
        path = self._dir / file
        data = json.loads(path.read_text()) if path.exists() else {}
        data[model] = entry
        path.write_text(json.dumps(data, indent=2))


class Run:
    """Load each contender once, forecast every task it is given, record timings and failures."""

    def __init__(self, root: Path, force: bool, threads: int):
        self._root = root
        self._force = force
        self._threads = threads

    def execute(self, contender, tasks: list[Windows]) -> None:
        stores = [Store(self._root, w.name) for w in tasks]
        for store, windows in zip(stores, tasks):
            store.keep_windows(windows)
        todo = [(s, w) for s, w in zip(stores, tasks) if self._force or not s.has(contender.name)]
        if not todo:
            print(f"{contender.name}: cached", flush=True)
            return
        try:
            load = contender.load()
        except Exception as e:  # noqa: BLE001 - a model that cannot load is recorded, not fatal
            for store, _ in todo:
                store.fail(contender.name, f"load: {e!r}\n{traceback.format_exc(limit=3)}")
            print(f"{contender.name}: LOAD FAILED {e!r}", flush=True)
            return
        for store, windows in todo:
            before = os.getloadavg()[0]
            start = time.perf_counter()
            try:
                q = contender.forecast(windows)
            except Exception as e:  # noqa: BLE001
                store.fail(contender.name, f"forecast: {e!r}\n{traceback.format_exc(limit=5)}")
                print(f"{contender.name} on {windows.name}: FAILED {e!r}", flush=True)
                continue
            seconds = time.perf_counter() - start
            q = np.asarray(q, dtype=float)
            if windows.freq in ("W-SUN", "D"):
                q = np.clip(q, 0.0, None)  # sales cannot be negative: applied to every contender
            problems = []
            if q.shape != (len(windows), windows.horizon, 9):
                problems.append(f"shape {q.shape}")
            if np.isnan(q).any():
                problems.append(f"{int(np.isnan(q).sum())} NaN")
            crossing = int((np.diff(q, axis=-1) < -1e-6).sum())
            timing = {
                "load_s": load,
                "forecast_s": seconds,
                "windows": len(windows),
                "s_per_window": seconds / len(windows),
                "torch_threads": self._threads,
                "loadavg_1min_before": before,
                "loadavg_1min_after": os.getloadavg()[0],
                "quantile_crossings_before_sort": crossing,
                "problems": problems,
                "finished_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds"),
            }
            describe = getattr(contender, "notes", None)
            if describe is not None:
                timing["model_notes"] = describe()
            store.keep(contender.name, np.sort(q, axis=-1), timing)
            print(f"{contender.name} on {windows.name}: {seconds:.1f}s for {len(windows)} windows "
                  f"(load {load:.1f}s, loadavg {before:.0f}) {problems or ''}", flush=True)
