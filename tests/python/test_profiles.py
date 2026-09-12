"""Analytic intensity-profile fixtures, independent of optical engines."""
import importlib
import math

import numpy as np
import pytest


def metrics(x, y, **kwargs):
    return importlib.import_module("_lib.profiles").profile_metrics(x, y, **kwargs)


def combine(rows, **kwargs):
    return importlib.import_module("_lib.profiles").combine_spectral_profiles(rows, **kwargs)


def test_gaussian_intensity_widths_and_cv_are_scale_invariant():
    x = np.linspace(-1, 1, 4001)
    w = .2
    intensity = np.exp(-2*(x/w)**2)
    a = metrics(x, intensity, profile_kind="cut")
    b = metrics(x, intensity*1e200, profile_kind="cut")
    assert a["status"] == "ok"
    assert a["fwhm_mm"] == pytest.approx(math.sqrt(2*math.log(2))*w, abs=2e-6)
    assert a["d1e2_mm"] == pytest.approx(2*w, abs=2e-6)
    assert a["connected_segments_fwhm"] == 1
    assert a["connected_segments_1e2"] == 1
    roi = intensity[np.abs(x) <= .21]
    assert a["cv_roi"] == pytest.approx(np.std(roi, ddof=0)/np.mean(roi), rel=1e-13)
    for key in ("fwhm_mm", "d1e2_mm", "cv_roi"):
        assert b[key] == pytest.approx(a[key], rel=1e-13)
    assert a["profile_kind"] == "cut"


def test_sampled_top_hat_uses_interpolated_edges_and_zero_roi_cv():
    sample = np.arange(-1000, 1001)
    x = sample/1000
    y = (np.abs(sample) <= 300).astype(float)
    out = metrics(x, y)
    # Sampled top-hat: plateau ends at +/-0.300, zero at +/-0.301.
    assert out["fwhm_mm"] == pytest.approx(.601)
    assert out["d1e2_mm"] == pytest.approx(.602-.002*math.exp(-2))
    assert out["cv_roi"] == 0


def test_separated_lobes_use_outermost_crossings_and_report_two_segments():
    x = np.linspace(-1, 1, 10001)
    w = .08
    y = np.exp(-2*((x-.4)/w)**2) + np.exp(-2*((x+.4)/w)**2)
    out = metrics(x, y)
    assert out["fwhm_mm"] == pytest.approx(.8+math.sqrt(2*math.log(2))*w, abs=2e-6)
    assert out["d1e2_mm"] == pytest.approx(.8+2*w, abs=2e-6)
    assert out["connected_segments_fwhm"] == 2
    assert out["connected_segments_1e2"] == 2


def test_truncated_profile_has_unavailable_crossings_not_clamped_widths():
    x = np.linspace(-.1, .1, 101)
    out = metrics(x, np.exp(-2*(x/.2)**2))
    assert out["fwhm_mm"] is None and out["d1e2_mm"] is None
    assert out["fwhm_status"] == "missing_crossings"
    assert out["d1e2_status"] == "missing_crossings"
    assert out["cv_roi"] is None and out["cv_roi_status"] == "roi_not_covered"
    assert out["status"] == "unavailable"
    assert any("edge" in w for w in out["warnings"])


def test_fixed_roi_is_not_recentered_on_peak_and_requires_adequate_samples():
    x = np.linspace(-1, 1, 1001)
    y = np.exp(-2*((x-.25)/.2)**2)
    out = metrics(x, y)
    roi = y[np.abs(x) <= .21]
    assert out["cv_roi"] == pytest.approx(np.std(roi)/np.mean(roi))
    coarse = metrics(np.linspace(-1, 1, 9), np.ones(9))
    assert coarse["cv_roi"] is None and coarse["cv_roi_status"] == "undersampled"
    assert any("sampling" in w for w in coarse["warnings"])


@pytest.mark.parametrize("x,y", [
    ([0, 1, 2], [0, float("nan"), 1]), ([0, 1, 2], [0, -1, 1]),
    ([0, 1, 2], [0, 0, 0]), ([0, 1, 1], [0, 1, 0]),
    ([0, 2, 1], [0, 1, 0]), ([0, 1], [1]),
    ([0, float("inf")], [1, 1]), ([0, 1], [1+1j, 1]),
])
def test_invalid_profiles_raise_value_error(x, y):
    with pytest.raises(ValueError):
        metrics(x, y)


def test_identical_spectral_grids_preserve_absolute_intensity_and_weights():
    x = np.linspace(-1, 1, 101)
    a = 3*np.exp(-2*(x/.3)**2)
    b = 7*np.exp(-2*((x-.1)/.2)**2)
    out = combine([{"x_mm": x, "intensity": a, "weight": 2},
                   {"x_mm": x, "intensity": b, "weight": 4}])
    np.testing.assert_array_equal(out["x_mm"], x)
    np.testing.assert_allclose(out["intensity"], 2*a+4*b, rtol=1e-15)
    assert out["weight_sum"] == 6
    assert out["normalization"] == "none_absolute_weighted_sum"
    assert out["interpolation"]["performed"] is False


def test_shifted_grids_combine_affine_intensity_exactly_on_overlap():
    # Affine functions have exact linear interpolants on any monotone grid.
    x1 = np.linspace(-1, 1, 101)
    x2 = np.linspace(-.95, 1.05, 83)
    out = combine([{"x_mm": x1, "intensity": 2+x1, "weight": .3},
                   {"x_mm": x2, "intensity": 3-2*x2, "weight": .7}])
    grid = np.asarray(out["x_mm"])
    assert grid[0] == -.95 and grid[-1] == 1
    assert out["interpolation"]["performed"] is True
    assert out["interpolation"]["extrapolation"] is False
    np.testing.assert_allclose(out["intensity"], .3*(2+grid)+.7*(3-2*grid), atol=1e-14)


def test_shared_grid_is_preserved_and_zero_weight_does_not_reduce_coverage():
    x = np.linspace(-1, 1, 101)
    shared = np.linspace(-.8, .8, 41)
    out = combine([{"x_mm": x, "intensity": 2+x, "weight": 1},
                   {"x_mm": [-.1, .1], "intensity": [1, 1], "weight": 0}], shared_grid=shared)
    np.testing.assert_array_equal(out["x_mm"], shared)
    np.testing.assert_allclose(out["intensity"], 2+shared)
    assert out["excluded_zero_weight_rows"] == [1]


@pytest.mark.parametrize("case", ["zero", "negative", "infinite", "no_overlap", "extrapolation"])
def test_invalid_spectral_combinations_fail(case):
    rows = [{"x_mm": [-1, 0, 1], "intensity": [1, 2, 1], "weight": 1}]
    kwargs = {}
    if case == "zero":
        rows[0]["weight"] = 0
    elif case == "negative":
        rows[0]["weight"] = -1
    elif case == "infinite":
        rows[0]["weight"] = float("inf")
    elif case == "no_overlap":
        rows.append({"x_mm": [2, 3], "intensity": [1, 1], "weight": 1})
    else:
        kwargs["shared_grid"] = [-2, 0, 2]
    with pytest.raises(ValueError):
        combine(rows, **kwargs)


def test_cuts_and_marginals_cannot_be_mixed():
    rows = [{"x_mm": [-1, 0, 1], "intensity": [1, 2, 1], "weight": 1,
             "profile_kind": kind} for kind in ("cut", "marginal")]
    with pytest.raises(ValueError, match="kind"):
        combine(rows)


def test_zero_roi_mean_is_unavailable_and_nonuniform_grid_is_explicit():
    x = np.unique(np.r_[np.linspace(-1, 1, 101), -.555])
    y = (np.abs(x) > .3).astype(float)
    out = metrics(x, y, profile_kind="marginal")
    assert out["cv_roi"] is None and out["cv_roi_status"] == "zero_roi_mean"
    assert out["grid"]["uniform"] is False
    assert any("unweighted" in w for w in out["warnings"])
    assert out["profile_kind"] == "marginal"


def test_threshold_plateau_is_connected_and_crossing_at_edge_is_unavailable():
    x = np.arange(-5, 6)/10
    y = [0, 0, .5, 1, 1, .5, 1, 1, .5, 0, 0]
    out = metrics(x, y)
    assert out["connected_segments_fwhm"] == 1
    assert out["fwhm_mm"] == pytest.approx(.6)
    edge = metrics(x, [.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, .5])
    assert edge["fwhm_mm"] is None


def test_a_single_sample_spike_never_claims_adequate_width_sampling():
    out = metrics(np.linspace(-1, 1, 101), np.r_[np.zeros(50), 1, np.zeros(50)])
    assert out["fwhm_mm"] == pytest.approx(.02)
    assert out["fwhm_status"] == "undersampled"
    assert out["status"] == "partial"


def test_shifted_gaussians_preserve_absolute_spectral_amplitude():
    x1, x2 = np.linspace(-1, 1, 1001), np.linspace(-.997, 1.003, 801)
    rows = [{"x_mm": x, "intensity": amplitude*np.exp(-2*(x/.2)**2), "weight": weight,
             "profile_kind": "cut", "intensity_unit": "W/mm^2"}
            for x, amplitude, weight in [(x1, 3, .3), (x2, 7, .7)]]
    result = combine(rows)
    grid = np.asarray(result["x_mm"])
    np.testing.assert_allclose(result["intensity"], 5.8*np.exp(-2*(grid/.2)**2), atol=.0005)
    measured = metrics(result["x_mm"], result["intensity"], profile_kind=result["profile_kind"])
    assert measured["fwhm_mm"] == pytest.approx(math.sqrt(2*math.log(2))*.2, abs=.00003)
    assert result["intensity_unit"] == "W/mm^2"


@pytest.mark.parametrize("meta", [{"profile_kind": []}, {"intensity_unit": []}, {"intensity_unit": ""}])
def test_invalid_semantic_metadata_raises_value_error(meta):
    with pytest.raises(ValueError):
        combine([{"x_mm": [-1, 0, 1], "intensity": [1, 2, 1], "weight": 1, **meta}])


def test_spectral_provenance_retains_wavelength_identity():
    out = combine([{"x_mm": [-1, 0, 1], "intensity": [1, 2, 1], "weight": 1,
                    "wavelength_um": .532, "source": "synthetic fixture"}])
    assert out["input_profiles"][0]["wavelength_um"] == .532
    assert out["input_profiles"][0]["source"] == "synthetic fixture"


def test_spectral_sum_rejects_overflow_and_zero_combined_irradiance():
    for values, weight in [([1e308]*3, 2), ([0]*3, 1)]:
        with pytest.raises(ValueError):
            combine([{"x_mm": [-1, 0, 1], "intensity": values, "weight": weight}])


def _positioned_cut(position):
    return {"x_mm": [-1, 0, 1], "intensity": [1, 2, 1], "weight": 1,
            "profile_kind": "cut", "orthogonal_position_mm": position}


@pytest.mark.parametrize("position", [1e-11, float("nan"), float("inf"), True, None])
def test_spectral_cuts_reject_different_or_invalid_orthogonal_positions(position):
    with pytest.raises(ValueError, match="orthogonal"):
        combine([_positioned_cut(0), _positioned_cut(position)])


def test_spectral_cuts_require_positions_for_all_contributing_rows():
    missing = _positioned_cut(0)
    del missing["orthogonal_position_mm"]
    with pytest.raises(ValueError, match="orthogonal"):
        combine([_positioned_cut(0), missing])


def test_spectral_cut_positions_allow_only_absolute_roundoff_and_retain_provenance():
    out = combine([_positioned_cut(0), _positioned_cut(5e-13)])
    assert out["orthogonal_position_mm"] == 0
    assert out["orthogonal_position_tolerance_mm"] == 1e-12
    assert [p["orthogonal_position_mm"] for p in out["input_profiles"]] == [0, 5e-13]
    assert out["interpolation"]["performed"] is False
    np.testing.assert_array_equal(out["intensity"], [2, 4, 2])
    # Relative tolerance must not allow unequal cut locations at a large offset.
    with pytest.raises(ValueError, match="orthogonal"):
        combine([_positioned_cut(1e6), _positioned_cut(1e6+1e-5)])


def test_zero_weight_cut_does_not_impose_position_identity():
    zero = _positioned_cut(1)
    zero["weight"] = 0
    out = combine([_positioned_cut(0), zero])
    assert out["orthogonal_position_mm"] == 0
    assert out["input_profiles"][1]["orthogonal_position_mm"] == 1
    del zero["orthogonal_position_mm"]
    assert combine([_positioned_cut(0), zero])["orthogonal_position_mm"] == 0
