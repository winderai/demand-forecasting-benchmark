"""A small model of how GB national demand works, built from domain structure rather than learned.

demand(t) = level
          + daily activity shape: Fourier harmonics of the half-hour of the (UK local) day,
            separate for weekdays and weekends
          + heating: slope x max(0, threshold - daily mean temperature)
          [prior variant only: the daily shape and level drift with the annual daylight cycle,
           which carries lighting in winter and embedded solar in summer]

Two variants:

- `TheoryContext` fits every parameter from the forecast's own context, where the context can
  identify it: no daily shape from less than a day, separate weekday/weekend shapes only with a
  day of each, a heating slope only with three or more distinct heating days spanning 2 C.
- `TheoryPrior` estimates the structure once from calendar year 2024 and refits only the level
  (and, given a full day, a scale) from the context.

Quantiles are the median plus empirical quantiles of the fitting residuals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from forecastbench.metrics import LEVELS
from forecastbench.windows import Windows

LONDON = "Europe/London"
DEGREE_DAY_BASE = 15.5  # the UK's conventional heating degree-day base temperature, in C


class Calendar:
    """Half-hour of day, weekend flag and day of year in UK local time."""

    def __init__(self, dates: pd.DatetimeIndex):
        self._local = dates.tz_convert(LONDON) if dates.tz is not None else dates

    def phase(self) -> np.ndarray:
        return (self._local.hour * 2 + self._local.minute // 30).to_numpy() / 48.0

    def weekend(self) -> np.ndarray:
        return (self._local.dayofweek >= 5).astype(float)

    def season(self) -> np.ndarray:
        return 2 * np.pi * self._local.dayofyear.to_numpy() / 365.25


def harmonics(phase: np.ndarray, k: int) -> np.ndarray:
    cols = [np.ones_like(phase)]
    for i in range(1, k + 1):
        cols += [np.cos(2 * np.pi * i * phase), np.sin(2 * np.pi * i * phase)]
    return np.stack(cols, axis=1)


def heating(temperature: np.ndarray, threshold: float) -> np.ndarray:
    return np.clip(threshold - temperature, 0.0, None)


def least_squares(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    ok = np.isfinite(y)
    ridge = 1e-6 * np.eye(x.shape[1])
    return np.linalg.solve(x[ok].T @ x[ok] + ridge, x[ok].T @ y[ok])


def residual_quantiles(residuals: np.ndarray) -> np.ndarray:
    r = residuals[np.isfinite(residuals)]
    return np.quantile(r, LEVELS) - np.quantile(r, 0.5)


class PriorStructure:
    """The structure estimated from one year of demand and temperature (2024)."""

    def __init__(self, dates: pd.DatetimeIndex, demand: np.ndarray, temperature: np.ndarray, k: int,
                 thresholds: list[float]):
        self._dates = dates
        self._demand = demand
        self._temperature = temperature
        self._k = k
        self._thresholds = thresholds

    def design(self, dates: pd.DatetimeIndex, temperature: np.ndarray, threshold: float) -> np.ndarray:
        cal = Calendar(dates)
        h = harmonics(cal.phase(), self._k)
        s = cal.season()
        annual = np.stack([np.ones_like(s), np.cos(s), np.sin(s)], axis=1)
        shape = (h[:, :, None] * annual[:, None, :]).reshape(len(dates), -1)
        w = cal.weekend()[:, None]
        return np.hstack([shape * (1 - w), shape * w, heating(temperature, threshold)[:, None]])

    def fitted(self) -> dict:
        best = None
        for threshold in self._thresholds:
            x = self.design(self._dates, self._temperature, threshold)
            beta = least_squares(x, self._demand)
            resid = self._demand - x @ beta
            sse = float(np.nansum(resid ** 2))
            if best is None or sse < best["sse"]:
                best = {"threshold": threshold, "beta": beta, "sse": sse, "residuals": resid}
        best["heating_slope_mw_per_c"] = float(best["beta"][-1])
        best["residual_quantiles"] = residual_quantiles(best["residuals"])
        best["rmse_mw"] = float(np.sqrt(np.nanmean(best["residuals"] ** 2)))
        best["parameters"] = int(len(best["beta"]))
        return best


class TheoryPrior:
    """Structure from 2024; level (and scale, given a full day of context) refitted per forecast."""

    def __init__(self, name: str, structure: PriorStructure):
        self.name = name
        self._structure = structure
        self._fit = None

    def load(self) -> float:
        self._fit = self._structure.fitted()
        return 0.0

    def notes(self) -> dict:
        f = self._fit
        return {"threshold_c": f["threshold"], "heating_slope_mw_per_c": f["heating_slope_mw_per_c"],
                "in_sample_rmse_mw": f["rmse_mw"], "parameters": f["parameters"]}

    def forecast(self, windows: Windows) -> np.ndarray:
        f = self._fit
        out = np.zeros((len(windows), windows.horizon, len(LEVELS)))
        for i in range(len(windows)):
            n = len(windows.contexts[i])
            temp = windows.known[i][0]
            dates = windows.context_dates[i].append(windows.target_dates[i])
            base = self._structure.design(dates, temp, f["threshold"]) @ f["beta"]
            y = windows.contexts[i]
            ok = np.isfinite(y)
            if ok.sum() >= 48:
                a = np.vstack([np.ones(ok.sum()), base[:n][ok]]).T
                level, scale = np.linalg.lstsq(a, y[ok], rcond=None)[0]
                if scale <= 0:
                    level, scale = float(np.mean(y[ok] - base[:n][ok])), 1.0
            else:
                level, scale = float(np.mean(y[ok] - base[:n][ok])), 1.0
            median = level + scale * base[n:]
            out[i] = median[:, None] + scale * f["residual_quantiles"][None, :]
        return out


class TheoryContext:
    """Every parameter from the context alone, where the context can identify it."""

    def __init__(self, name: str, max_harmonics: int):
        self.name = name
        self._k = max_harmonics
        self.identified: list[dict] = []

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        out = np.zeros((len(windows), windows.horizon, len(LEVELS)))
        self.identified = []
        for i in range(len(windows)):
            y = windows.contexts[i]
            n = len(y)
            temp = windows.known[i][0]
            dates = windows.context_dates[i].append(windows.target_dates[i])
            cal = Calendar(dates)
            observed = np.isfinite(y)
            n_obs = int(observed.sum())
            k = 0 if n_obs < 48 else min(self._k, n_obs // 24)
            h = harmonics(cal.phase(), k)
            weekend = cal.weekend()
            split = (weekend[:n][observed].sum() >= 48) and ((1 - weekend[:n][observed]).sum() >= 48) and k > 0
            cols = [h * (1 - weekend)[:, None], h * weekend[:, None]] if split else [h]
            days = pd.Series(temp[:n][observed]).round(1)
            hdd = heating(days.to_numpy(), DEGREE_DAY_BASE)
            distinct = np.unique(hdd[hdd > 0])
            slope = len(distinct) >= 3 and (distinct.max() - distinct.min()) >= 2.0
            x = np.hstack(cols)
            if slope:
                x_h = np.hstack([x, heating(temp, DEGREE_DAY_BASE)[:, None]])
                beta = least_squares(x_h[:n], y)
                if beta[-1] < 0:
                    slope = False
                else:
                    x = x_h
            if not slope:
                beta = least_squares(x[:n], y)
            fitted = x[:n] @ beta
            q = residual_quantiles(y - fitted) if n_obs > 1 else np.zeros(len(LEVELS))
            out[i] = (x[n:] @ beta)[:, None] + q[None, :]
            self.identified.append({"harmonics": k, "weekday_weekend_split": bool(split),
                                    "heating_slope": float(beta[-1]) if slope else 0.0})
        return out

    def notes(self) -> dict:
        slopes = [r["heating_slope"] for r in self.identified]
        return {
            "windows": len(self.identified),
            "harmonics_used": sorted({r["harmonics"] for r in self.identified}),
            "weekday_weekend_split_windows": sum(r["weekday_weekend_split"] for r in self.identified),
            "heating_slope_identified_windows": sum(s > 0 for s in slopes),
            "heating_slope_mean_mw_per_c_when_identified": float(np.mean([s for s in slopes if s > 0])) if any(s > 0 for s in slopes) else 0.0,
        }
