#  test_geometry.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
"""Unit tests for the mask measurements.

These build masks directly rather than segmenting a photograph, so the expected
answer is known exactly and no model has to be downloaded to run them.
"""

import numpy as np
import pytest

from fusion_vision_mcp import geometry

SIZE = 200


def blank() -> np.ndarray:
    return np.zeros((SIZE, SIZE), dtype=bool)


def rect(x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    mask = blank()
    mask[y0:y1, x0:x1] = True
    return mask


def disc(cx: int, cy: int, radius: int) -> np.ndarray:
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    return ((xs - cx) ** 2 + (ys - cy) ** 2) <= radius**2


def test_separate_masks_report_the_distance_between_them() -> None:
    left = rect(10, 90, 30, 110)
    right = rect(70, 90, 90, 110)
    result = geometry.relation(left, right)

    assert result["state"] == "separate"
    assert result["gap"] == pytest.approx(40, abs=1.5)
    assert result["a_inside_b"] == 0.0


def test_masks_a_pixel_apart_count_as_touching() -> None:
    left = rect(10, 90, 50, 110)
    right = rect(51, 90, 90, 110)

    assert geometry.relation(left, right)["state"] == "touching"


def test_a_mask_fully_inside_another_reports_full_containment_and_depth() -> None:
    small = disc(100, 100, 10)
    large = disc(100, 100, 50)
    result = geometry.relation(small, large)

    assert result["state"] == "overlapping"
    assert result["a_inside_b"] == pytest.approx(1.0)
    assert result["b_inside_a"] < 0.1
    # Every pixel of the small disc is at least 40px from the large disc's edge.
    assert result["embed_depth"] > 35


def test_a_mask_overlapping_only_at_the_rim_is_shallow() -> None:
    """The signal that separates gripping a rim from being buried in a face."""
    large = disc(100, 100, 50)
    straddling = disc(148, 100, 10)
    deep = disc(100, 100, 10)

    shallow_result = geometry.relation(straddling, large)
    deep_result = geometry.relation(deep, large)

    assert shallow_result["state"] == "overlapping"
    assert shallow_result["embed_depth"] < deep_result["embed_depth"] / 3


def test_elongation_separates_a_bar_from_a_square() -> None:
    assert geometry.elongation(rect(10, 95, 190, 105)) > 8
    assert geometry.elongation(rect(80, 80, 120, 120)) == pytest.approx(1.0, abs=0.15)


def test_a_straight_bar_has_a_near_zero_deviation() -> None:
    result = geometry.straightness(rect(10, 95, 190, 105))

    assert result["max_deviation"] < 0.02
    assert result["kink"] < 0.02


def test_a_bent_bar_deviates_from_straight() -> None:
    mask = blank()
    for x in range(10, 100):
        mask[95 + (x - 10) // 3 : 105 + (x - 10) // 3, x] = True
    for x in range(100, 190):
        mask[125 - (x - 100) // 3 : 135 - (x - 100) // 3, x] = True

    assert geometry.straightness(mask)["max_deviation"] > 0.05


def test_width_profile_distinguishes_one_taper_from_two() -> None:
    """A blade tapers at the tip only; something pointed at both ends does not."""
    one_taper = blank()
    two_tapers = blank()
    for i, x in enumerate(range(20, 180)):
        half_a = max(1, (160 - i) // 12)
        one_taper[100 - half_a : 100 + half_a, x] = True
        half_b = max(1, int(12 - abs(i - 80) * 0.14))
        two_tapers[100 - half_b : 100 + half_b, x] = True

    single = geometry.width_profile(one_taper)
    double = geometry.width_profile(two_tapers)

    assert single["end_symmetry"] < 0.5
    assert double["end_symmetry"] > 0.7


def test_an_empty_mask_does_not_raise() -> None:
    result = geometry.relation(blank(), disc(100, 100, 10))

    assert result["state"] == "empty"
    assert np.isnan(result["gap"])


def test_describe_reports_every_metric() -> None:
    result = geometry.describe(rect(10, 95, 190, 105))

    assert result["area"] == 180 * 10
    assert set(result) == {"area", "elongation", "straightness", "width_profile"}
