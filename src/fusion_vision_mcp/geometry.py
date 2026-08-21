#  geometry.py
#
#  Copyright (c) 2025-2026 Junpei Kawamoto
#
#  This software is released under the MIT License.
#
#  http://opensource.org/licenses/mit-license.php
"""Geometric measurements over segmentation masks.

Language models judge images semantically but estimate quantities poorly: whether
two things *touch*, how far apart they are, or how deeply one is buried inside
another are exactly the questions they answer unreliably by eye. These functions
turn a pair of masks into numbers so the caller can apply its own judgement to a
measurement rather than to an impression.

Pure numpy/scipy — no model loading — so every function here is cheap to test in
isolation from Florence-2, Moondream or SAM2.

A note on what is measurable: the metrics below are aggregate statistics over a
mask (principal axes, band centroids, overlap fractions, distance transforms).
They deliberately avoid the medial axis / skeleton, which is unstable on the
rough silhouettes typical of photographic subjects: a single bump on the contour
spawns a spurious branch, and that noise swamps the signal being measured.
"""

from __future__ import annotations

from typing import Any, Final

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import distance_transform_edt

Mask = NDArray[np.bool_]

#: Bands used when profiling an object along its long axis.
_PROFILE_BINS: Final[int] = 20

#: Fraction of the long axis averaged together when measuring width at one end.
_END_BAND: Final[float] = 0.08

#: Masks closer than this (in image pixels) are reported as touching rather than
#: separate. SAM2 decodes at a fixed 256x256 grid, so boundaries carry roughly a
#: pixel of slop once upscaled; treating a sub-pixel gap as contact avoids
#: reporting a "gap" that is really just resampling error.
_TOUCH_TOLERANCE_PX: Final[float] = 2.0


def _principal_frame(mask: Mask) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Project a mask's pixels onto its own long and short axes.

    Returns ``(along, across, eigenvalues)`` where ``along`` runs down the
    object's longest extent and ``across`` is perpendicular to it.
    """
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], axis=1).astype(np.float64)
    pts -= pts.mean(axis=0)
    cov = np.cov(pts.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    axis = eigvecs[:, int(np.argmax(eigvals))]
    perp = np.array([-axis[1], axis[0]])
    return pts @ axis, pts @ perp, eigvals


def elongation(mask: Mask) -> float:
    """How long-and-thin an object is: 1.0 is circular, higher is more elongated."""
    if mask.sum() < 10:
        return float("nan")
    _, _, eigvals = _principal_frame(mask)
    return float(np.sqrt(max(eigvals) / max(float(min(eigvals)), 1e-9)))


def width_profile(mask: Mask) -> dict[str, float]:
    """Width at each end of the long axis, and at the middle.

    Distinguishes shapes that taper once from shapes that taper at both ends.
    A blade tapers to a point at the tip and stops at a wider hilt; something
    pointed at *both* ends has a different signature even when it is a single
    connected region that no object detector would split in two.

    ``end_symmetry`` is ``min(end_a, end_b) / max(end_a, end_b)``: near 1.0 means
    both ends are equally wide, near 0 means one end is far narrower.
    """
    if mask.sum() < 50:
        return {
            "end_a_width": float("nan"),
            "mid_width": float("nan"),
            "end_b_width": float("nan"),
            "end_symmetry": float("nan"),
        }

    along, across, _ = _principal_frame(mask)
    lo, hi = float(along.min()), float(along.max())
    span = hi - lo

    def width_at(position: float) -> float:
        band = (along >= position - span * _END_BAND) & (along <= position + span * _END_BAND)
        return float(across[band].max() - across[band].min()) if band.any() else 0.0

    end_a, end_b = width_at(lo), width_at(hi)
    widest = max(end_a, end_b)
    return {
        "end_a_width": end_a,
        "mid_width": width_at((lo + hi) / 2),
        "end_b_width": end_b,
        "end_symmetry": (min(end_a, end_b) / widest) if widest > 0 else float("nan"),
    }


def straightness(mask: Mask, bins: int = _PROFILE_BINS) -> dict[str, float]:
    """How far an object's centreline strays from straight, and from a smooth curve.

    The centreline is built from the centroid of each band across the long axis,
    so every point averages the object's full width there and surface texture
    cancels out.

    ``max_deviation`` is the largest offset from a straight line, as a fraction of
    the object's length: a straight rod is near 0, a banana is large. ``kink`` is
    the largest offset from a fitted *quadratic*, which a smoothly bent object
    still fits well — so a high ``kink`` with a low ``max_deviation`` points at an
    abrupt local direction change rather than an overall bow.
    """
    empty = {"max_deviation": float("nan"), "kink": float("nan")}
    if mask.sum() < 50:
        return empty

    along, across, _ = _principal_frame(mask)
    edges = np.linspace(along.min(), along.max(), bins + 1)
    centres_a, centres_c = [], []
    for i in range(bins):
        band = (along >= edges[i]) & (along <= edges[i + 1])
        if band.sum() > 5:
            centres_a.append(float(along[band].mean()))
            centres_c.append(float(across[band].mean()))
    if len(centres_a) < 5:
        return empty

    a = np.asarray(centres_a)
    c = np.asarray(centres_c)
    length = float(a.max() - a.min())
    if length <= 0:
        return empty

    linear = np.polyval(np.polyfit(a, c, 1), a)
    quadratic = np.polyval(np.polyfit(a, c, 2), a)
    return {
        "max_deviation": float(np.abs(c - linear).max()) / length,
        "kink": float(np.abs(c - quadratic).max()) / length,
    }


def relation(a: Mask, b: Mask) -> dict[str, Any]:
    """Measure how two masks sit relative to each other.

    ``state`` is one of ``separate``, ``touching`` or ``overlapping``.

    ``gap`` is the shortest distance between them in pixels, and is ``0.0`` once
    they overlap. Two things that ought to be in contact — a hand and the grip it
    holds — but report a gap of tens of pixels are not in contact.

    ``a_inside_b`` / ``b_inside_a`` give the share of one mask's area falling
    within the other. ``embed_depth`` is how far inside the overlapping pixels
    reach, measured to the nearest boundary of ``b``: a hand curled around a
    shield's rim overlaps it shallowly, while a hand fused into the middle of the
    shield face overlaps it deeply. Depth is what separates the two cases; the
    overlap fraction alone does not.
    """
    area_a, area_b = int(a.sum()), int(b.sum())
    if area_a == 0 or area_b == 0:
        return {
            "state": "empty",
            "gap": float("nan"),
            "a_inside_b": float("nan"),
            "b_inside_a": float("nan"),
            "embed_depth": float("nan"),
        }

    both = a & b
    if not both.any():
        gap = float(distance_transform_edt(~b)[a].min())
        return {
            "state": "touching" if gap <= _TOUCH_TOLERANCE_PX else "separate",
            "gap": gap,
            "a_inside_b": 0.0,
            "b_inside_a": 0.0,
            "embed_depth": 0.0,
        }

    return {
        "state": "overlapping",
        "gap": 0.0,
        "a_inside_b": float(both.sum()) / area_a,
        "b_inside_a": float(both.sum()) / area_b,
        "embed_depth": float(distance_transform_edt(b)[both].mean()),
    }


def describe(mask: Mask) -> dict[str, Any]:
    """Shape metrics for a single object."""
    return {
        "area": int(mask.sum()),
        "elongation": elongation(mask),
        "straightness": straightness(mask),
        "width_profile": width_profile(mask),
    }
