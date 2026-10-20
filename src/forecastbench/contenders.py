"""The forecasters under test. Each returns quantiles at levels 0.1..0.9, shape (windows, horizon, 9).

Every contender has a `name`, a `load()` that returns seconds spent loading (0 for fitted models),
and a `forecast(windows)` that returns the quantile array. The median (level 0.5, index 4) is every
model's point forecast.

Model libraries are imported inside each contender, not at the top of this module: LightGBM's and
torch's OpenMP runtimes crash each other in one process on macOS, so scripts/run.py runs the
classical and the neural contenders in separate processes and each must import only its own.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from forecastbench.metrics import LEVELS
from forecastbench.windows import Windows

MEDIAN = 4
INTERVALS = [20, 40, 60, 80]


def degenerate(point: np.ndarray) -> np.ndarray:
    """A point forecast as nine identical quantiles."""
    return np.repeat(point[..., None], len(LEVELS), axis=-1)


def interpolated(series: np.ndarray) -> np.ndarray:
    s = pd.Series(series, dtype=float)
    return s.interpolate(limit_direction="both").to_numpy()


def left_padded(rows: list[np.ndarray], width: int | None = None) -> np.ndarray:
    """Stack rows of different lengths, right-aligned, NaN on the left."""
    n = width if width is not None else max(r.shape[-1] for r in rows)
    lead = rows[0].shape[:-1]
    out = np.full((len(rows), *lead, n), np.nan, dtype=np.float32)
    for i, r in enumerate(rows):
        out[i, ..., n - r.shape[-1]:] = r[..., -n:]
    return out


def from_intervals(frame: pd.DataFrame, column: str) -> np.ndarray:
    """statsforecast / mlforecast lo-/hi- columns at 20/40/60/80% to quantiles 0.1..0.9."""
    cols = [f"{column}-lo-80", f"{column}-lo-60", f"{column}-lo-40", f"{column}-lo-20", column,
            f"{column}-hi-20", f"{column}-hi-40", f"{column}-hi-60", f"{column}-hi-80"]
    return frame[cols].to_numpy(dtype=float)


class Batches:
    """Indices of windows grouped into batches of similar context length."""

    def __init__(self, windows: Windows, size: int):
        self._windows = windows
        self._size = size

    def __iter__(self):
        order = np.argsort([len(c) for c in self._windows.contexts], kind="stable")
        for i in range(0, len(order), self._size):
            yield order[i:i + self._size]


class SeasonalNaive:
    """Same step one season ago; the last value when the history is shorter than a season."""

    def __init__(self, name: str, season: int):
        self.name = name
        self._season = season

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        h = windows.horizon
        out = np.zeros((len(windows), h))
        for i, c in enumerate(windows.contexts):
            c = interpolated(c)
            if len(c) >= self._season:
                idx = len(c) - self._season + (np.arange(h) % self._season)
                out[i] = c[idx]
            else:
                out[i] = c[-1]
        return degenerate(out)


class Statistical:
    """A statsforecast model fitted per window (AutoETS with intervals; Croston/TSB point only)."""

    def __init__(self, name: str, model, column: str, freq: str, jobs: int, intervals: bool):
        self.name = name
        self._model = model
        self._column = column
        self._freq = freq
        self._jobs = jobs
        self._intervals = intervals
        self.chosen: dict[str, int] = {}

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        from statsforecast import StatsForecast

        frame = windows.frame()
        frame["y"] = frame.groupby("unique_id")["y"].transform(lambda s: s.interpolate(limit_direction="both"))
        sf = StatsForecast(models=[self._model], freq=self._freq, n_jobs=self._jobs)
        if self._intervals:
            result = sf.forecast(df=frame, h=windows.horizon, level=INTERVALS, fitted=False)
        else:
            result = sf.forecast(df=frame, h=windows.horizon)
        result = result.set_index("unique_id").loc[windows.keys()]
        h = windows.horizon
        if self._intervals:
            q = from_intervals(result.reset_index(), self._column).reshape(len(windows), h, len(LEVELS))
            return np.sort(q, axis=-1)
        return degenerate(result[self._column].to_numpy(dtype=float).reshape(len(windows), h))


class RetailLightGBM:
    """Global LightGBM over every series at a cut-off: direct multi-horizon quantile models."""

    def __init__(self, name: str, lags: list[int], estimators: int, threads: int, seed: int):
        self.name = name
        self._lags = lags
        self._estimators = estimators
        self._threads = threads
        self._seed = seed

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        import lightgbm as lgb
        from mlforecast import MLForecast
        from mlforecast.lag_transforms import ExpandingMean, RollingMean

        h = windows.horizon
        out = np.zeros((len(windows), h, len(LEVELS)))
        frame = windows.frame()
        frame["series"] = frame["unique_id"].str.split("|").str[0]
        cutoffs = np.array([c.isoformat() for c in windows.cutoffs])
        for cutoff in sorted(set(cutoffs)):
            rows = np.where(cutoffs == cutoff)[0]
            keys = [windows.keys()[i] for i in rows]
            train = frame[frame["unique_id"].isin(keys)].copy()
            longest = int(train.groupby("unique_id").size().max())
            lags = [lag for lag in self._lags if lag < longest]
            models = {
                f"q{level:.1f}": lgb.LGBMRegressor(
                    objective="quantile", alpha=float(level), n_estimators=self._estimators,
                    learning_rate=0.05, num_leaves=31, min_child_samples=20, subsample=0.8, subsample_freq=1,
                    colsample_bytree=0.8, n_jobs=self._threads, random_state=self._seed, verbose=-1,
                )
                for level in LEVELS
            }
            mlf = MLForecast(
                models=models,
                freq=windows.freq,
                lags=lags,
                lag_transforms={1: [RollingMean(window_size=4), RollingMean(window_size=13), ExpandingMean()]},
                date_features=[week_of_year, "month"],
            )
            mlf.fit(train[["unique_id", "ds", "y"]], max_horizon=h, dropna=False)
            pred = mlf.predict(h=h).set_index("unique_id").loc[keys]
            q = pred[list(models)].to_numpy(dtype=float).reshape(len(rows), h, len(LEVELS))
            out[rows] = np.sort(q, axis=-1)
        return out


def week_of_year(dates: pd.DatetimeIndex) -> np.ndarray:
    return dates.isocalendar().week.to_numpy(dtype=int)


def half_hour(dates: pd.DatetimeIndex) -> np.ndarray:
    local = dates.tz_convert("Europe/London") if dates.tz is not None else dates
    return (local.hour * 2 + local.minute // 30).to_numpy()


def day_of_week(dates: pd.DatetimeIndex) -> np.ndarray:
    local = dates.tz_convert("Europe/London") if dates.tz is not None else dates
    return local.dayofweek.to_numpy()


def day_of_year(dates: pd.DatetimeIndex) -> np.ndarray:
    local = dates.tz_convert("Europe/London") if dates.tz is not None else dates
    return local.dayofyear.to_numpy()


class GridLightGBM:
    """LightGBM on the one national series, refitted at every cut-off.

    Lags start at one day, so the 48-step forecast never feeds on its own predictions and each
    quantile model forecasts directly. Calendar features plus (optionally) the temperature covariate.
    """

    def __init__(self, name: str, backtest, days: int | None, lags: list[int], estimators: int,
                 threads: int, seed: int, temperature: bool):
        self.name = name
        self._backtest = backtest
        self._days = days
        self._lags = lags
        self._estimators = estimators
        self._threads = threads
        self._seed = seed
        self._temperature = temperature

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        import lightgbm as lgb
        from mlforecast import MLForecast
        from mlforecast.lag_transforms import RollingMean

        h = windows.horizon
        out = np.zeros((len(windows), h, len(LEVELS)))
        for i, (cutoff, context, dates) in enumerate(zip(windows.cutoffs, windows.contexts, windows.context_dates)):
            if self._days is None:
                train = pd.DataFrame({"ds": dates, "y": interpolated(context)})
                if self._temperature:
                    train["temperature"] = windows.known[i][0, : len(context)]
            else:
                train = self._backtest.training(cutoff, self._days)
                train["y"] = interpolated(train["y"].to_numpy())
            train["unique_id"] = "GB-ND"
            lags = [lag for lag in self._lags if lag < len(train)]
            transforms = {48: [RollingMean(window_size=48), RollingMean(window_size=336)]}
            transforms = {k: [t for t in v if t.window_size + k <= len(train)] for k, v in transforms.items()}
            transforms = {k: v for k, v in transforms.items() if v and k < len(train)}
            models = {
                f"q{level:.1f}": lgb.LGBMRegressor(
                    objective="quantile", alpha=float(level), n_estimators=self._estimators,
                    learning_rate=0.05, num_leaves=31, min_child_samples=20, subsample=0.8, subsample_freq=1,
                    colsample_bytree=0.8, n_jobs=self._threads, random_state=self._seed, verbose=-1,
                )
                for level in LEVELS
            }
            mlf = MLForecast(
                models=models, freq="30min", lags=lags, lag_transforms=transforms,
                date_features=[half_hour, day_of_week, day_of_year],
            )
            columns = ["unique_id", "ds", "y"] + (["temperature"] if self._temperature else [])
            mlf.fit(train[columns], dropna=False, static_features=[])
            future = pd.DataFrame({"unique_id": "GB-ND", "ds": windows.target_dates[i]})
            if self._temperature:
                future["temperature"] = windows.known[i][0, len(context):]
                pred = mlf.predict(h=h, X_df=future)
            else:
                pred = mlf.predict(h=h)
            out[i] = np.sort(pred[list(models)].to_numpy(dtype=float), axis=-1)
        return out


class Timestral:
    def __init__(self, name: str, repo: str, batch: int, covariates: bool):
        self.name = name
        self._repo = repo
        self._batch = batch
        self._covariates = covariates
        self._model = None

    def load(self) -> float:
        from timestral import TimestralForecaster

        start = time.perf_counter()
        self._model = TimestralForecaster.from_pretrained(self._repo, device="cpu", local_files_only=True)
        return time.perf_counter() - start

    def forecast(self, windows: Windows) -> np.ndarray:
        levels = list(self._model.quantile_levels)
        pick = [min(range(len(levels)), key=lambda j: abs(levels[j] - q)) for q in LEVELS]
        out = np.zeros((len(windows), windows.horizon, len(LEVELS)))
        for idx in Batches(windows, self._batch):
            ctx = left_padded([windows.contexts[i] for i in idx])
            known = None
            if self._covariates and windows.known is not None:
                known = left_padded([windows.known[i] for i in idx], ctx.shape[-1] + windows.horizon)
            f = self._model.forecast(ctx, prediction_length=windows.horizon, known_covariates=known)
            out[idx] = f.quantiles[:, 0][..., pick].cpu().numpy()
        return out


class Chronos2:
    def __init__(self, name: str, repo: str, batch: int, covariates: bool):
        self.name = name
        self._repo = repo
        self._batch = batch
        self._covariates = covariates
        self._pipeline = None

    def load(self) -> float:
        from chronos import Chronos2Pipeline

        start = time.perf_counter()
        self._pipeline = Chronos2Pipeline.from_pretrained(self._repo, device_map="cpu")
        return time.perf_counter() - start

    def forecast(self, windows: Windows) -> np.ndarray:
        h = windows.horizon
        if self._covariates and windows.known is not None:
            inputs = []
            for c, k in zip(windows.contexts, windows.known):
                n = len(c)
                inputs.append({
                    "target": c.astype(np.float32),
                    "past_covariates": {name: k[j, :n] for j, name in enumerate(windows.known_names)},
                    "future_covariates": {name: k[j, n:] for j, name in enumerate(windows.known_names)},
                })
        else:
            inputs = [c.astype(np.float32) for c in windows.contexts]
        quantiles, _ = self._pipeline.predict_quantiles(
            inputs, prediction_length=h, quantile_levels=[float(q) for q in LEVELS], batch_size=self._batch,
        )
        return np.stack([q[0].numpy() for q in quantiles])


class TimesFM25:
    """TimesFM 2.5 with the flags from its model card. Covariates need XReg (JAX), so none here."""

    def __init__(self, name: str, repo: str, context: int, batch: int):
        self.name = name
        self._repo = repo
        self._context = context
        self._batch = batch
        self._model = None

    def load(self) -> float:
        import timesfm

        start = time.perf_counter()
        self._model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(self._repo, torch_compile=False)
        self._model.compile(
            timesfm.ForecastConfig(
                max_context=self._context, max_horizon=128, normalize_inputs=True,
                use_continuous_quantile_head=True, force_flip_invariance=True, infer_is_positive=True,
                fix_quantile_crossing=True, per_core_batch_size=self._batch,
            )
        )
        return time.perf_counter() - start

    def forecast(self, windows: Windows) -> np.ndarray:
        _, quantiles = self._model.forecast(horizon=windows.horizon, inputs=[c.astype(float) for c in windows.contexts])
        return np.asarray(quantiles)[:, :, 1:10]


class TimesFM3:
    """TimesFM 3.0 through its benchmark evaluator defaults (symmetric averaging, non-negativity)."""

    def __init__(self, name: str, repo: str, batch: int, covariates: bool):
        self.name = name
        self._repo = repo
        self._batch = batch
        self._covariates = covariates
        self._model = None

    def load(self) -> float:
        from timesfm3 import ModelConfig, TimesFM3Evaluator

        start = time.perf_counter()
        self._model = TimesFM3Evaluator(ModelConfig(checkpoint_path=self._repo, per_core_batch_size=self._batch, device="cpu"))
        return time.perf_counter() - start

    def forecast(self, windows: Windows) -> np.ndarray:
        contexts = [c.astype(np.float32) for c in windows.contexts]
        pf = None
        if self._covariates and windows.known is not None:
            pf = [k.astype(np.float32) for k in windows.known]
        outs = list(self._model.predict_batch(
            contexts, horizon=windows.horizon, past_future_covariates=pf, return_quantiles=True,
        ))
        return np.stack([np.atleast_3d(o.quantiles).reshape(windows.horizon, len(LEVELS)) for o in outs])


class T0:
    """The Forecasting Company's t0 with its four recommended adjustments switched on."""

    def __init__(self, name: str, repo: str, batch: int, covariates: bool):
        self.name = name
        self._repo = repo
        self._batch = batch
        self._covariates = covariates
        self._model = None

    def load(self) -> float:
        from t0 import T0Forecaster

        start = time.perf_counter()
        self._model = T0Forecaster.from_pretrained(self._repo).eval()
        return time.perf_counter() - start

    def forecast(self, windows: Windows) -> np.ndarray:
        import torch

        out = np.zeros((len(windows), windows.horizon, len(LEVELS)))
        for idx in Batches(windows, self._batch):
            ctx = left_padded([windows.contexts[i] for i in idx])
            fut = None
            if self._covariates and windows.known is not None:
                fut = torch.from_numpy(left_padded([windows.known[i] for i in idx], ctx.shape[-1] + windows.horizon))
            with torch.inference_mode():
                f = self._model.predict(
                    torch.from_numpy(ctx), horizon=windows.horizon, quantile_levels=[float(q) for q in LEVELS],
                    future_covariates=fut, trim_leading_missing=True, symmetric_averaging=True,
                    clip_nonnegative=True, snap_integers=True,
                )
            out[idx] = np.asarray(f.quantiles.cpu().numpy())
        return out


class PanelLightGBM:
    """Global LightGBM over a daily panel with lags of at least the horizon, so it forecasts in one shot,
    using the windows' known-in-advance covariates (discount, holiday, activity) when asked."""

    def __init__(self, name: str, lags: list[int], estimators: int, threads: int, seed: int, covariates: bool):
        self.name = name
        self._lags = lags
        self._estimators = estimators
        self._threads = threads
        self._seed = seed
        self._covariates = covariates

    def load(self) -> float:
        return 0.0

    def forecast(self, windows: Windows) -> np.ndarray:
        import lightgbm as lgb
        from mlforecast import MLForecast
        from mlforecast.lag_transforms import RollingMean

        h = windows.horizon
        keys = windows.keys()
        train, future = [], []
        for i, key in enumerate(keys):
            n = len(windows.contexts[i])
            part = pd.DataFrame({"unique_id": key, "ds": windows.context_dates[i], "y": windows.contexts[i]})
            ahead = pd.DataFrame({"unique_id": key, "ds": windows.target_dates[i]})
            if self._covariates:
                for j, name in enumerate(windows.known_names):
                    part[name] = windows.known[i][j, :n]
                    ahead[name] = windows.known[i][j, n:]
            train.append(part)
            future.append(ahead)
        models = {
            f"q{level:.1f}": lgb.LGBMRegressor(
                objective="quantile", alpha=float(level), n_estimators=self._estimators, learning_rate=0.05,
                num_leaves=31, min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                n_jobs=self._threads, random_state=self._seed, verbose=-1,
            )
            for level in LEVELS
        }
        mlf = MLForecast(models=models, freq=windows.freq, lags=self._lags,
                         lag_transforms={h: [RollingMean(window_size=7), RollingMean(window_size=28)]},
                         date_features=["dayofweek"])
        mlf.fit(pd.concat(train, ignore_index=True), dropna=False, static_features=[])
        if self._covariates:
            pred = mlf.predict(h=h, X_df=pd.concat(future, ignore_index=True))
        else:
            pred = mlf.predict(h=h)
        pred = pred.set_index("unique_id").loc[keys]
        q = pred[list(models)].to_numpy(dtype=float).reshape(len(keys), h, len(LEVELS))
        return np.sort(q, axis=-1)
