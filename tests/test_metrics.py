import math

import numpy as np

from forecastbench import metrics


def test_scale_uses_seasonal_differences():
    # |3-1| + |4-2| + |5-3| over 3 differences at period 2 = 2
    assert metrics.scale(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), 2) == 2.0


def test_scale_falls_back_to_period_one_on_short_history():
    # period 52 longer than history: |2-1| + |4-2| = 3 over 2 = 1.5
    assert metrics.scale(np.array([1.0, 2.0, 4.0]), 52) == 1.5


def test_mase_by_hand():
    history = np.array([10.0, 12.0, 11.0, 13.0])  # period 1 differences 2, 1, 2 -> scale 5/3
    target = np.array([14.0, 12.0])
    point = np.array([13.0, 14.0])  # errors 1, 2 -> MAE 1.5
    assert math.isclose(metrics.mase(target, point, history, 1), 1.5 / (5 / 3))


def test_mase_skips_missing_targets():
    history = np.array([0.0, 2.0])
    assert metrics.mase(np.array([1.0, np.nan]), np.array([2.0, 100.0]), history, 1) == 0.5


def test_quantile_loss_by_hand():
    target = np.array([10.0])
    quantiles = np.array([[8.0, 12.0]])
    levels = np.array([0.1, 0.9])
    # level 0.1, forecast 8 below 10: 2 * 0.1 * 2 = 0.4
    # level 0.9, forecast 12 above 10: 2 * (1 - 0.9) * 2 = 0.4
    loss = metrics.quantile_loss(target, quantiles, levels)
    assert np.allclose(loss, [0.4, 0.4])


def test_wql_by_hand():
    target = np.array([10.0, 20.0])
    quantiles = np.array([[10.0], [10.0]])  # median forecast 10 for both
    levels = np.array([0.5])
    # pinball: 0 and 0.5 * 10 = 5, times two = 10, over sum |y| = 30
    assert math.isclose(metrics.wql(target, quantiles, levels), 10 / 30)


def test_wql_equals_mae_over_mean_for_a_point_forecast_at_the_median():
    target = np.array([3.0, 5.0, 9.0])
    point = np.array([4.0, 4.0, 4.0])
    q = np.repeat(point[:, None], 1, axis=1)
    assert math.isclose(metrics.wql(target, q, np.array([0.5])), np.sum(np.abs(target - point)) / np.sum(target))


def test_coverage_by_hand():
    target = np.array([1.0, 5.0, 9.0, np.nan])
    lower = np.array([0.0, 6.0, 8.0, 0.0])
    upper = np.array([2.0, 7.0, 10.0, 0.0])
    assert metrics.coverage(target, lower, upper) == 2 / 3


def test_geometric_mean_ratio_skips_zero_pairs():
    ratio, n = metrics.geometric_mean_ratio(np.array([2.0, 0.5, 1.0]), np.array([1.0, 1.0, 0.0]))
    assert n == 2 and math.isclose(ratio, 1.0)


def test_newsvendor_by_hand():
    short, excess = metrics.newsvendor(np.array([10.0, 3.0, np.nan]), np.array([7.0, 5.0, 1.0]))
    assert (short, excess) == (3.0, 2.0)
