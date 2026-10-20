"""Backtest windows: one (series, cut-off) pair each, with its context, target and covariates."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Windows:
    """A batch of forecasting problems sharing a horizon and a frequency.

    `contexts[i]` is the history up to and including the cut-off, oldest first, possibly of
    different lengths. `known[i]`, when present, is `(C, len(contexts[i]) + horizon)`.
    `history[i]` is the history used for the MASE scale, which can be longer than the context
    (the history-length sweep scales every truncation by the same full history).
    """

    name: str
    freq: str
    horizon: int
    period: int
    ids: list[str]
    cutoffs: list[pd.Timestamp]
    contexts: list[np.ndarray]
    targets: np.ndarray
    target_dates: list[pd.DatetimeIndex]
    history: list[np.ndarray]
    known: list[np.ndarray] | None = None
    known_names: list[str] = field(default_factory=list)
    context_dates: list[pd.DatetimeIndex] | None = None

    def __len__(self) -> int:
        return len(self.ids)

    def named(self, name: str) -> "Windows":
        return replace(self, name=name)

    def without_covariates(self, name: str) -> "Windows":
        return Windows(
            name, self.freq, self.horizon, self.period, self.ids, self.cutoffs, self.contexts,
            self.targets, self.target_dates, self.history, None, [], self.context_dates,
        )

    def truncated(self, name: str, length: int) -> "Windows":
        """The same targets with every context cut to its last `length` steps."""
        contexts = [c[-length:] for c in self.contexts]
        known = None
        if self.known is not None:
            known = [k[:, -(length + self.horizon):] for k in self.known]
        dates = None if self.context_dates is None else [d[-length:] for d in self.context_dates]
        return Windows(
            name, self.freq, self.horizon, self.period, self.ids, self.cutoffs, contexts,
            self.targets, self.target_dates, self.history, known, self.known_names, dates,
        )

    def frame(self) -> pd.DataFrame:
        """Long frame of every context (unique_id = series|cutoff), for statsforecast / mlforecast."""
        parts = []
        for i, key in enumerate(self.keys()):
            parts.append(pd.DataFrame({"unique_id": key, "ds": self.context_dates[i], "y": self.contexts[i]}))
        return pd.concat(parts, ignore_index=True)

    def keys(self) -> list[str]:
        return [f"{s}|{c.isoformat()}" for s, c in zip(self.ids, self.cutoffs)]


def christmas_covariates(dates: pd.DatetimeIndex) -> np.ndarray:
    """Known-in-advance calendar rows for weekly retail: a Nov-Dec peak flag and week of year / 52."""
    peak = dates.month.isin([11, 12]).astype(float)
    week = dates.isocalendar().week.to_numpy(dtype=float) / 52.0
    return np.stack([peak, week])


class RetailBacktest:
    """Rolling-origin windows over the weekly retail panel."""

    def __init__(self, frame: pd.DataFrame, horizon: int, min_history: int, live_weeks: int):
        self._frame = frame
        self._horizon = horizon
        self._min_history = min_history
        self._live = live_weeks

    def eligible(self, cutoffs: list[pd.Timestamp]) -> pd.DataFrame:
        """(product, cut-off) pairs with enough history, a sale in the last `live` weeks, nonzero scale."""
        rows = []
        for code, g in self._frame.groupby("unique_id", sort=True):
            ds = g["ds"].to_numpy()
            y = g["y"].to_numpy()
            for c in cutoffs:
                n = int(np.sum(ds <= np.datetime64(c)))
                if n < self._min_history:
                    continue
                ctx = y[:n]
                if ctx[-self._live:].sum() <= 0 or np.all(ctx == ctx[0]):
                    continue
                rows.append({"unique_id": code, "cutoff": c, "history": n})
        return pd.DataFrame(rows)

    def windows(self, name: str, pairs: pd.DataFrame, calendar: bool) -> Windows:
        groups = {k: g for k, g in self._frame.groupby("unique_id", sort=False)}
        ids, cutoffs, contexts, targets, tdates, cdates, known = [], [], [], [], [], [], []
        h = self._horizon
        for row in pairs.itertuples(index=False):
            g = groups[row.unique_id]
            n = int(row.history)
            y = g["y"].to_numpy(dtype=float)
            ds = pd.DatetimeIndex(g["ds"])
            ids.append(row.unique_id)
            cutoffs.append(pd.Timestamp(row.cutoff))
            contexts.append(y[:n])
            targets.append(y[n:n + h])
            tdates.append(ds[n:n + h])
            cdates.append(ds[:n])
            if calendar:
                known.append(christmas_covariates(ds[: n + h]))
        return Windows(
            name, "W-SUN", h, 1, ids, cutoffs, contexts, np.array(targets), tdates, list(contexts),
            known if calendar else None, ["nov_dec_peak", "week_of_year"] if calendar else [], cdates,
        )


class GridBacktest:
    """Day-ahead windows over the half-hourly national demand series."""

    def __init__(self, frame: pd.DataFrame, horizon: int, context: int, history: int):
        self._frame = frame.set_index("ds")
        self._horizon = horizon
        self._context = context
        self._history = history

    def windows(self, name: str, cutoffs: list[pd.Timestamp]) -> Windows:
        """Each cut-off is the first half-hour forecast (local midnight); context ends just before it."""
        y = self._frame["ND"]
        t = self._frame["temperature"]
        index = self._frame.index
        ids, cuts, contexts, targets, tdates, cdates, known, history = [], [], [], [], [], [], [], []
        for c in cutoffs:
            pos = index.get_loc(c)
            ctx = y.iloc[pos - self._context:pos].to_numpy(dtype=float)
            tgt = y.iloc[pos:pos + self._horizon].to_numpy(dtype=float)
            ids.append("GB-ND")
            cuts.append(c)
            contexts.append(ctx)
            targets.append(tgt)
            tdates.append(index[pos:pos + self._horizon])
            cdates.append(index[pos - self._context:pos])
            known.append(t.iloc[pos - self._context:pos + self._horizon].to_numpy(dtype=float)[None, :])
            history.append(y.iloc[max(0, pos - self._history):pos].to_numpy(dtype=float))
        return Windows(
            name, "30min", self._horizon, 48, ids, cuts, contexts, np.array(targets), tdates, history,
            known, ["temperature"], cdates,
        )

    def training(self, cutoff: pd.Timestamp, days: int) -> pd.DataFrame:
        """The fitted models' training frame: `days` of history before the cut-off."""
        start = cutoff - pd.Timedelta(days=days)
        f = self._frame.loc[(self._frame.index >= start) & (self._frame.index < cutoff)]
        return pd.DataFrame({"ds": f.index, "y": f["ND"].to_numpy(), "temperature": f["temperature"].to_numpy()})

    def future(self, cutoff: pd.Timestamp) -> pd.DataFrame:
        pos = self._frame.index.get_loc(cutoff)
        f = self._frame.iloc[pos:pos + self._horizon]
        return pd.DataFrame({"ds": f.index, "temperature": f["temperature"].to_numpy()})
