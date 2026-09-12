"""One-dimensional *intensity* metrics and incoherent spectral profile sums.

Widths use the outermost crossings of a piecewise-linear sampled intensity, relative
to its sampled peak. They are not Gaussian fits, beam second moments or lobe widths.
CV is population standard deviation / mean of original samples in a fixed ROI.
Sampling checks are minimum diagnostics, not a proof of convergence.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

KINDS = {"cut", "marginal", "unspecified"}
MIN_ROI_SAMPLES = 5
MIN_COMPONENT_SAMPLES = 3
EDGE_FRACTION_WARNING = 1e-3
ORTHOGONAL_POSITION_TOLERANCE_MM = 1e-12


def _array(values, name):
    raw = np.asarray(values)
    if np.iscomplexobj(raw) or raw.dtype.kind == "b":
        raise ValueError(f"{name} must contain real numbers, not complex or boolean values")
    try:
        result = np.asarray(values, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain finite real numbers") from exc
    if result.ndim != 1 or len(result) < 2 or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a one-dimensional array of at least two finite samples")
    return result


def _grid(values):
    x = _array(values, "x_mm")
    with np.errstate(over="ignore", invalid="ignore"):
        dx = np.diff(x)
        span = x[-1] - x[0]
    if not np.isfinite(dx).all() or not np.isfinite(span) or np.any(dx <= 0):
        raise ValueError("x_mm must be strictly increasing with a finite positive span")
    return x


def _profile(x_mm, intensity, *, allow_zero=False):
    x, y = _grid(x_mm), _array(intensity, "intensity")
    if x.shape != y.shape or np.any(y < 0):
        raise ValueError("intensity must match x_mm and be nonnegative")
    if not allow_zero and not y.max() > 0:
        raise ValueError("intensity must not be all zero")
    return x, y


def _finite(value, name, *, positive=False):
    try:
        valid = not isinstance(value, (bool, np.bool_)) and np.isscalar(value) and math.isfinite(value)
    except (TypeError, ValueError, OverflowError):
        valid = False
    if not valid or (positive and value <= 0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return float(value)


def _grid_info(x):
    dx = np.diff(x)
    return {"sample_count": int(x.size), "bounds_mm": [float(x[0]), float(x[-1])],
            "min_step_mm": float(dx.min()), "max_step_mm": float(dx.max()),
            "uniform": bool(np.allclose(dx, np.median(dx), rtol=1e-6, atol=0))}


def _threshold(x, normalized, level):
    above = normalized >= level
    starts = np.flatnonzero(above & np.r_[True, ~above[:-1]])
    ends = np.flatnonzero(above & np.r_[~above[1:], True])
    left, right = int(starts[0]), int(ends[-1])
    counts = (ends - starts + 1).tolist()
    def crossing(i):
        # The endpoints bracket the level; this never extrapolates or clamps.
        fraction = (level-normalized[i])/(normalized[i+1]-normalized[i])
        return float(x[i] + fraction*(x[i+1]-x[i]))
    lo = crossing(left-1) if left > 0 else None
    hi = crossing(right) if right < len(x)-1 else None
    missing = lo is None or hi is None
    status = "missing_crossings" if missing else "undersampled" if min(counts) < MIN_COMPONENT_SAMPLES else "ok"
    return {"width_mm": None if missing else hi-lo, "status": status,
            "level_fraction": level, "left_crossing_mm": lo, "right_crossing_mm": hi,
            "connected_segments": len(starts), "samples_per_segment": counts}


def profile_metrics(x_mm, intensity, roi_half_width_mm=.21, *, profile_kind="unspecified") -> dict:
    """Measure an intensity cut or marginal without silently converting between them.

    The fixed ROI is [-roi_half_width_mm,+roi_half_width_mm] in supplied coordinates;
    no peak recentering occurs. CV requires full coverage, >=5 original ROI samples,
    and no gap across the ROI larger than one quarter of its width. Widths with fewer
    than three samples in a threshold component retain their interpolated value but
    have ``undersampled`` status. Missing threshold crossings always produce None.
    """
    x, y = _profile(x_mm, intensity)
    half = _finite(roi_half_width_mm, "roi_half_width_mm", positive=True)
    if not isinstance(profile_kind, str) or profile_kind not in KINDS:
        raise ValueError(f"profile_kind must be one of {sorted(KINDS)}")
    peak = float(y.max())
    normalized = y / peak
    grid = _grid_info(x)
    warnings = []
    if not grid["uniform"]:
        warnings.append("nonuniform grid: CV uses unweighted sample statistics, not a spatially weighted integral")
    if profile_kind == "unspecified":
        warnings.append("profile kind unspecified: identify an intensity cut or an integrated marginal before comparing results")
    edges = [float(normalized[0]), float(normalized[-1])]
    if max(edges) >= EDGE_FRACTION_WARNING:
        warnings.append("edge intensity is non-negligible relative to sampled peak; check window convergence and truncation")
    threshold = {"fwhm": _threshold(x, normalized, .5), "1e2": _threshold(x, normalized, math.exp(-2))}
    for name, detail in threshold.items():
        if detail["status"] == "missing_crossings":
            warnings.append(f"{name}: missing outer threshold crossings at grid edge; width unavailable")
        elif detail["status"] == "undersampled":
            warnings.append(f"{name}: inadequate sampling in a threshold component; refine the source grid")
    inside = (x >= -half) & (x <= half)
    count = int(inside.sum())
    covered = bool(x[0] <= -half and x[-1] >= half)
    gaps = np.diff(np.r_[-half, x[inside], half])
    max_gap = float(gaps.max())
    cv = None
    if not covered:
        cv_status = "roi_not_covered"
        warnings.append("ROI is not fully covered by the grid; CV unavailable")
    elif count < MIN_ROI_SAMPLES or max_gap > half/2*(1+1e-12):
        cv_status = "undersampled"
        warnings.append("inadequate ROI sampling: need >=5 samples and maximum gap <= one quarter ROI width; CV unavailable")
    elif not np.max(y[inside]) > 0:
        cv_status = "zero_roi_mean"
        warnings.append("ROI mean intensity is zero; CV unavailable")
    else:
        roi = y[inside] / np.max(y[inside])  # Stable, mathematically scale-invariant CV.
        cv = float(np.std(roi, ddof=0) / np.mean(roi))
        cv_status = "ok"
    fwhm, d1e2 = threshold["fwhm"], threshold["1e2"]
    values = [fwhm["width_mm"], d1e2["width_mm"], cv]
    statuses = [fwhm["status"], d1e2["status"], cv_status]
    status = "unavailable" if all(v is None for v in values) else "ok" if all(s == "ok" for s in statuses) else "partial"
    return {"status": status, "profile_kind": profile_kind, "intensity_semantics": "intensity_not_field_amplitude",
            "fwhm_mm": fwhm["width_mm"], "d1e2_mm": d1e2["width_mm"], "cv_roi": cv,
            "fwhm_status": fwhm["status"], "d1e2_status": d1e2["status"], "cv_roi_status": cv_status,
            "connected_segments_fwhm": fwhm["connected_segments"], "connected_segments_1e2": d1e2["connected_segments"],
            "threshold_details": threshold, "grid": grid, "peak_intensity": peak,
            "peak_x_mm": float(x[int(np.argmax(y))]), "edge_fraction_of_peak": edges,
            "roi": {"bounds_mm": [-half, half], "fully_covered": covered, "sample_count": count,
                    "max_gap_mm": max_gap, "cv_convention": "population_std_ddof0_over_mean_of_original_roi_samples"},
            "sampling_policy": {"min_roi_samples": MIN_ROI_SAMPLES,
                                "max_roi_gap_fraction": .25, "min_threshold_component_samples": MIN_COMPONENT_SAMPLES},
            "edge_warning_fraction": EDGE_FRACTION_WARNING, "warnings": warnings,
            "method": "outermost linearly interpolated sampled-peak intensity threshold crossings; no extrapolation, peak fit, recentering, or width clamping"}


def _digest(a):
    return hashlib.sha256(np.asarray(a, dtype="<f8").tobytes()).hexdigest()


def combine_spectral_profiles(rows, shared_grid=None) -> dict:
    """Incoherent sum of absolute intensities times the supplied spectral weights.

    Weights are not normalized. There is no per-row peak, integral, or power scaling.
    Default grid is the union of source coordinates in the positive-weight overlap;
    a caller-supplied grid must be fully contained there. Linear interpolation is
    intentional, pointwise and not an energy-conserving rebinning operation. Cuts and
    marginals must be combined separately; optional profile_kind/intensity_unit metadata
    must agree across all contributing rows. Mutually coherent fields require another API.
    If any contributing cut declares orthogonal_position_mm, all must declare finite
    positions spanning at most 1e-12 mm (absolute numerical roundoff, no relative tolerance).
    Output retains the first contributing position and all original positions; there is
    no interpolation perpendicular to a cut. Zero-weight rows do not impose identity.
    """
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a nonempty list of spectral profiles")
    parsed, provenance, excluded = [], [], []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not {"x_mm", "intensity", "weight"} <= row.keys():
            raise ValueError("each spectral profile requires x_mm, intensity and weight")
        x, y = _profile(row["x_mm"], row["intensity"], allow_zero=True)
        weight = _finite(row["weight"], "spectral weight")
        if weight < 0:
            raise ValueError("spectral weight cannot be negative")
        kind = row.get("profile_kind", "unspecified")
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError("invalid spectral profile kind")
        unit = row.get("intensity_unit", "unspecified")
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError("intensity_unit must be a nonempty string")
        provenance.append({"row": index, "weight": weight, "grid": _grid_info(x),
                           "x_sha256_float64_le": _digest(x), "intensity_sha256_float64_le": _digest(y),
                           "profile_kind": kind, "intensity_unit": unit})
        if "wavelength_um" in row:
            provenance[-1]["wavelength_um"] = _finite(row["wavelength_um"], "wavelength_um", positive=True)
        if "source" in row:
            if not isinstance(row["source"], str) or not row["source"].strip():
                raise ValueError("source identity must be a nonempty string")
            provenance[-1]["source"] = row["source"]
        if "orthogonal_position_mm" in row:
            provenance[-1]["orthogonal_position_mm"] = _finite(row["orthogonal_position_mm"], "orthogonal_position_mm")
        if weight == 0:
            excluded.append(index)
        else:
            parsed.append((x, y, weight, index))
    if not parsed:
        raise ValueError("at least one spectral weight must be positive")
    kinds = {provenance[i]["profile_kind"] for _, _, _, i in parsed}
    units = {provenance[i]["intensity_unit"] for _, _, _, i in parsed}
    if len(kinds) != 1 or len(units) != 1:
        raise ValueError("contributing spectral profiles must have matching kind and intensity units")
    position_metadata = {}
    contributing = [provenance[i] for _, _, _, i in parsed]
    if kinds == {"cut"} and any("orthogonal_position_mm" in p for p in contributing):
        if not all("orthogonal_position_mm" in p for p in contributing):
            raise ValueError("all contributing cuts must declare orthogonal_position_mm")
        positions = [p["orthogonal_position_mm"] for p in contributing]
        if max(positions)-min(positions) > ORTHOGONAL_POSITION_TOLERANCE_MM:
            raise ValueError("contributing cuts have different orthogonal positions; perpendicular interpolation is unsupported")
        position_metadata = {"orthogonal_position_mm": positions[0],
                             "orthogonal_position_tolerance_mm": ORTHOGONAL_POSITION_TOLERANCE_MM}
    lower, upper = max(x[0] for x, *_ in parsed), min(x[-1] for x, *_ in parsed)
    if lower >= upper:
        raise ValueError("spectral grids have no nonzero common overlap")
    if shared_grid is None:
        grid = np.unique(np.concatenate([x[(x >= lower) & (x <= upper)] for x, *_ in parsed]))
        grid_policy = "source_coordinate_union_on_common_overlap"
    else:
        grid = _grid(shared_grid)
        grid_policy = "caller_supplied_within_common_overlap"
        if grid[0] < lower or grid[-1] > upper:
            raise ValueError("shared_grid requires extrapolation outside common overlap")
    if len(grid) < 2:
        raise ValueError("common overlap does not contain enough grid samples")
    total = np.zeros_like(grid)
    interpolated = []
    with np.errstate(over="ignore", invalid="ignore"):
        for x, y, weight, index in parsed:
            # A subset consisting entirely of original nodes needs no interpolation.
            locations = np.searchsorted(x, grid)
            exact = np.array_equal(x[locations], grid)
            values = y[locations] if exact else np.interp(grid, x, y)
            if not exact:
                interpolated.append(index)
            provenance[index]["interpolated"] = not exact
            total += weight*values
    weight_sum = sum(weight for _, _, weight, _ in parsed)
    if not np.isfinite(total).all() or not math.isfinite(weight_sum):
        raise ValueError("spectral weighted sum overflow; rescale absolute units or weights")
    if not total.max() > 0:
        raise ValueError("combined spectral intensity is all zero")
    return {"x_mm": grid.tolist(), "intensity": total.tolist(), "weight_sum": weight_sum, **position_metadata,
            "normalization": "none_absolute_weighted_sum", "profile_kind": kinds.pop(), "intensity_unit": units.pop(),
            "combination": "incoherent_intensity_sum", "common_overlap_mm": [float(lower), float(upper)],
            "grid": _grid_info(grid), "grid_policy": grid_policy, "excluded_zero_weight_rows": excluded,
            "interpolation": {"performed": bool(interpolated), "rows": interpolated,
                              "method": "piecewise_linear_pointwise", "extrapolation": False,
                              "conserves_integrated_power": False},
            "input_profiles": provenance,
            "warnings": (["source grids differ: intentional pointwise interpolation; verify sampling convergence"] if interpolated else [])}
