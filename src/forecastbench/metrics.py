"""Forecast accuracy metrics, following the GIFT-Eval / GluonTS definitions.

Every function takes plain NumPy arrays. NaN in a target marks an unobserved value and is skipped.
"""

from __future__ import annotations

import numpy as np

LEVELS = np.round(np.arange(0.1, 1.0, 0.1), 1)


def scale(history: np.ndarray, period: int) -> float:
    """MASE denominator: mean absolute seasonal difference of the in-sample history.

    Falls back to period 1 when the history is shorter than period + 1, as GluonTS does.
    """
    h = np.asarray(history, dtype=float)
    h = h[~np.isnan(h)]
    m = period if len(h) > period else 1
    if len(h) <= m:
        return float("nan")
    return float(np.mean(np.abs(h[m:] - h[:-m])))


def absolute_error(target: np.ndarray, point: np.ndarray) -> float:
    ok = ~np.isnan(target)
    return float(np.sum(np.abs(target[ok] - point[ok])))


def mase(target: np.ndarray, point: np.ndarray, history: np.ndarray, period: int) -> float:
    ok = ~np.isnan(target)
    s = scale(history, period)
    if not ok.any() or not np.isfinite(s) or s == 0:
        return float("nan")
    return float(np.mean(np.abs(target[ok] - point[ok])) / s)


def quantile_loss(target: np.ndarray, quantiles: np.ndarray, levels: np.ndarray = LEVELS) -> np.ndarray:
    """Summed pinball loss per level, times two (the GluonTS convention): shape (len(levels),)."""
    ok = ~np.isnan(target)
    y = target[ok][:, None]
    q = quantiles[ok]
    return 2.0 * np.sum(np.abs((y - q) * ((y <= q).astype(float) - levels[None, :])), axis=0)


def wql(target: np.ndarray, quantiles: np.ndarray, levels: np.ndarray = LEVELS) -> float:
    """Mean weighted quantile loss: mean over levels of 2 * sum(pinball) / sum(|y|)."""
    ok = ~np.isnan(target)
    denominator = np.sum(np.abs(target[ok]))
    if denominator == 0:
        return float("nan")
    return float(np.mean(quantile_loss(target, quantiles, levels)) / denominator)


def coverage(target: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    ok = ~np.isnan(target)
    y = target[ok]
    return float(np.mean((y >= lower[ok]) & (y <= upper[ok])))


def geometric_mean_ratio(model: np.ndarray, baseline: np.ndarray) -> tuple[float, int]:
    """Geometric mean of model / baseline over pairs where both are finite and positive."""
    m = np.asarray(model, dtype=float)
    b = np.asarray(baseline, dtype=float)
    ok = np.isfinite(m) & np.isfinite(b) & (m > 0) & (b > 0)
    if not ok.any():
        return float("nan"), 0
    return float(np.exp(np.mean(np.log(m[ok] / b[ok])))), int(ok.sum())


def newsvendor(target: np.ndarray, order: np.ndarray) -> tuple[float, float]:
    """Units short (demand above the order) and units left over (order above demand)."""
    ok = ~np.isnan(target)
    gap = target[ok] - order[ok]
    return float(np.sum(np.clip(gap, 0, None))), float(np.sum(np.clip(-gap, 0, None)))
