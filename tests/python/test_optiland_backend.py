"""Portable integration checks; optiland==0.6.2 runs in an isolated uv environment."""
import hashlib
import json
import math

import pytest
from _lib.design_contract import DesignSpec


def _adapter():
    from _lib.optiland_backend import OptilandBackend
    return OptilandBackend


@pytest.fixture
def singlet(tmp_path):
    pytest.importorskip("optiland", reason="run with --with optiland==0.6.2")
    from optiland import optic
    from optiland.fileio import save_optiland_file
    from optiland.materials import IdealMaterial
    lens = optic.Optic()
    lens.surfaces.add(index=0, thickness=math.inf)
    lens.surfaces.add(index=1, radius=50, thickness=5,
                      material=IdealMaterial(n=1.5, k=0), is_stop=True)
    lens.surfaces.add(index=2, radius=-50, thickness=49.152542372881356)
    lens.surfaces.add(index=3)
    lens.set_aperture(aperture_type="EPD", value=2)
    lens.fields.set_type(field_type="angle")
    lens.fields.add(y=0)
    lens.fields.add(y=1)
    lens.wavelengths.add(value=0.55, is_primary=True)
    lens.wavelengths.add(value=0.65)
    path = tmp_path / "singlet.json"
    save_optiland_file(lens, path)
    return path


def _spec(requirements=None, **analysis):
    return DesignSpec.from_dict({"schema": "1", "fields": [1, 2], "wavelengths": [1, 2],
                                "frequencies_cyc_per_mm": [10, 100000], "analysis": analysis,
                                "requirements": requirements or [
                                    {"id": "efl", "metric": "efl_mm", "unit": "mm", "min": 40},
                                    {"id": "fno", "metric": "f_number", "unit": "1", "min": 20},
                                    {"id": "track", "metric": "total_track_mm", "unit": "mm", "max": 60},
                                    {"id": "gap", "metric": "image_distance_mm", "unit": "mm", "max": 60},
                                    {"id": "spot", "metric": "rms_spot_um", "unit": "um",
                                     "field": 1, "wavelength": 1, "max": 1},
                                ]})


@pytest.mark.tier1
def test_singlet_paraxial_values_match_thick_lens_formula(singlet):
    # Power=(n-1)*(1/R1-1/R2+(n-1)*t/(n*R1*R2)) = 59/3000 mm^-1.
    with _adapter()(singlet) as backend:
        rows = {row["metric"]: row for row in backend.evaluate(_spec())}
        assert rows["efl_mm"]["value"] == pytest.approx(50.847457627118644, rel=1e-10)
        assert rows["f_number"]["value"] == pytest.approx(25.423728813559322, rel=1e-10)
        assert rows["total_track_mm"]["value"] == pytest.approx(54.152542372881356)
        assert rows["image_distance_mm"]["value"] == pytest.approx(49.152542372881356)
        assert 0 < rows["rms_spot_um"]["value"] < 1


@pytest.mark.tier1
def test_focus_improves_spot_and_preserves_invariants_source_and_reload(singlet, tmp_path):
    original = hashlib.sha256(singlet.read_bytes()).hexdigest()
    with _adapter()(singlet) as backend:
        before = backend.inspect()
        json.dumps(before, allow_nan=False)
        backend.set_focus(51.152542372881356)
        bad = backend.evaluate(_spec())[-1]["value"]
        assert bad > 10
        assert backend.inspect()["invariants"] == before["invariants"]
        backend.set_focus(49.152542372881356)
        good = backend.evaluate(_spec())[-1]["value"]
        assert good < bad / 10
        saved = tmp_path / "candidate.json"
        backend.save(saved)
        backend.set_focus(52)
        backend.load(saved)
        assert backend.inspect()["focus_mm"] == pytest.approx(49.152542372881356)
        assert backend.inspect()["invariants"] == before["invariants"]
        assert backend.evaluate(_spec())[-1]["value"] == pytest.approx(good, rel=1e-10)
        with pytest.raises(ValueError, match="source"):
            backend.save(singlet)
    assert hashlib.sha256(singlet.read_bytes()).hexdigest() == original
    with pytest.raises(RuntimeError, match="open"):
        backend.inspect()


@pytest.mark.tier1
def test_inspection_retains_image_axial_position_independently_of_focus_gap(singlet):
    with _adapter()(singlet) as backend:
        before = backend.inspect()
        assert before['axial_positions_mm'][1:] == pytest.approx([0, 5, 54.152542372881356])
        backend.lens.surfaces[-1].geometry.cs.z += .125
        after = backend.inspect()
        assert after['focus_mm'] == before['focus_mm']
        assert after['axial_positions_mm'][-1] == pytest.approx(before['axial_positions_mm'][-1] + .125)


@pytest.mark.tier1
def test_fft_mtf_near_diffraction_limit_and_declares_interpolation(singlet):
    requirements = [{"id": axis, "metric": "mtf", "unit": "1", "min": 0,
                     "field": 1, "wavelength": 1, "frequency": 10, "axis": axis}
                    for axis in ("tangential", "sagittal")]
    with _adapter()(singlet) as backend:
        rows = backend.evaluate(_spec(requirements, sampling=64))
    # Circular clear pupil, q = frequency * wavelength_mm * F-number.
    q = 10 * 0.00055 * 25.423728813559322
    expected = 2 / math.pi * (math.acos(q) - q * math.sqrt(1 - q * q))
    for row in rows:
        assert row["value"] == pytest.approx(expected, abs=0.02)
        assert row["analysis"]["interpolation"] == "linear, no extrapolation"
        assert row["field"] == 1 and row["wavelength"] == 1


@pytest.mark.tier1
@pytest.mark.parametrize("kind", ["polarization", "field", "frequency"])
def test_unavailable_analysis_returns_identified_null_row(singlet, kind):
    requirement = {"id": "m", "metric": "mtf", "unit": "1", "min": 0,
                   "field": 1, "wavelength": 1, "frequency": 10, "axis": "tangential"}
    spec = _spec([requirement], use_polarization=kind == "polarization")
    if kind == "field":
        spec.data["requirements"][0]["field"] = 99
    if kind == "frequency":
        spec.data["requirements"][0]["frequency"] = 100000
    with _adapter()(singlet) as backend:
        row = backend.evaluate(spec)[0]
    assert row["value"] is None
    assert row["reason"]
    assert row["metric"] == "mtf" and row["axis"] == "tangential" and row["wavelength"] == 1


@pytest.mark.tier1
@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, True])
def test_focus_rejects_invalid_distance_without_mutating(singlet, value):
    with _adapter()(singlet) as backend:
        before = backend.inspect()
        with pytest.raises(ValueError):
            backend.set_focus(value)
        assert backend.inspect() == before


@pytest.mark.tier1
@pytest.mark.parametrize("change", ["pickup", "asphere", "decenter", "polarization", "coating"])
def test_native_unsupported_features_rejected_before_analysis(singlet, change):
    data = json.loads(singlet.read_text())
    if change == "pickup":
        data["pickups"] = [{"type": "unknown"}]
    elif change == "asphere":
        data["surface_group"]["surfaces"][1]["geometry"]["conic"] = -1
    elif change == "decenter":
        data["surface_group"]["surfaces"][1]["geometry"]["cs"]["x"] = 1
    elif change == "polarization":
        data["wavelengths"]["polarization"] = "unpolarized"
    else:
        data["surface_group"]["surfaces"][1]["interaction_model"]["coating"] = {"type": "unknown"}
    singlet.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="unsupported"), _adapter()(singlet):
        pytest.fail("unsupported native model opened")


ZMX = """VERS 190513 80 123457 L123457
MODE SEQ
UNIT MM X W X CM MR CPMM
NAME Restricted singlet
GCAT SCHOTT
ENPD 2
FTYP 0 0 1 1 0 0 0
XFLN 0
YFLN 0
WAVM 1 0.55 1
PWAV 1
SURF 0
TYPE STANDARD
CURV 0
DISZ INFINITY
SURF 1
TYPE STANDARD
STOP
CURV 0.02
DISZ 5
GLAS N-BK7 0 0
SURF 2
TYPE STANDARD
CURV -0.02
DISZ 47.6
SURF 3
TYPE STANDARD
CURV 0
DISZ 0
"""


@pytest.mark.parametrize("directive", ["TYPE EVENASPH", "TYPE COORDBRK", "MNUM 2", "THIC 1 2", "PICK 1 2", "UNKNOWN 1"])
def test_zemax_rejects_unsupported_directives_before_engine_loading(tmp_path, directive):
    from _lib.optiland_backend import validate_zemax
    path = tmp_path / "unsupported.zmx"
    path.write_text(ZMX + directive + "\n")
    with pytest.raises(ValueError, match="unsupported"):
        validate_zemax(path)


@pytest.mark.tier1
def test_restricted_zemax_import_matches_prescription_and_records_limits(tmp_path):
    pytest.importorskip("optiland")
    path = tmp_path / "singlet.zmx"
    path.write_text(ZMX)
    with _adapter()(path) as backend:
        state = backend.inspect()
        assert state["focus_mm"] == pytest.approx(47.6)
        assert state["engine"]["version"] == "0.6.2"
        assert state["import_restrictions"]
        assert state["prescription"][1]["radius_mm"] == 50
        assert state["prescription"][2]["radius_mm"] == -50
        backend.save(tmp_path / "imported.json")


@pytest.mark.tier1
def test_parameter_edits_change_optics_and_move_downstream_surfaces(singlet):
    with _adapter()(singlet) as backend:
        assert backend.model_suffix == ".json"
        assert backend.get_parameter(1, "radius_mm") == 50
        backend.set_parameter(1, "radius_mm", 60)
        assert backend.evaluate(_spec())[0]["value"] == pytest.approx(55.38461538461539, rel=1e-10)
        backend.set_parameter(1, "radius_mm", 50)
        backend.set_parameter(1, "thickness_mm", 6)
        assert backend.get_parameter(1, "thickness_mm") == 6
        assert backend.evaluate(_spec())[2]["value"] == pytest.approx(55.152542372881356)
        assert backend.inspect()["focus_mm"] == pytest.approx(49.152542372881356)


@pytest.mark.tier1
def test_field_and_wavelength_indices_retain_physical_identity(singlet):
    requirements = [{"id": f"mtf-{field}-{wave}", "metric": "mtf", "unit": "1", "min": 0,
                     "field": field, "wavelength": wave, "frequency": 10, "axis": "tangential"}
                    for field, wave in [(2, 2), (1, 1), (2, 1), (1, 2)]]
    with _adapter()(singlet) as backend:
        rows = backend.evaluate(_spec(requirements))
    assert [(r["field"], r["wavelength"], r["analysis"]["field_xy_deg"], r["analysis"]["wavelength_um"])
            for r in rows] == [(2, 2, [0, 1], 0.65), (1, 1, [0, 0], 0.55),
                               (2, 1, [0, 1], 0.55), (1, 2, [0, 0], 0.65)]
    assert rows[1]["value"] > rows[3]["value"]  # Longer wavelength has lower diffraction MTF.


@pytest.mark.tier1
@pytest.mark.parametrize("change", ["nan_radius", "inconsistent_position", "negative_epd", "negative_weight"])
def test_invalid_native_geometry_or_weights_are_rejected(singlet, change):
    data = json.loads(singlet.read_text())
    if change == "nan_radius":
        data["surface_group"]["surfaces"][1]["geometry"]["radius"] = math.nan
    elif change == "inconsistent_position":
        data["surface_group"]["surfaces"][2]["geometry"]["cs"]["z"] = 20
    elif change == "negative_epd":
        data["aperture"]["value"] = -2
    else:
        data["fields"]["fields"][0]["weight"] = -1
    singlet.write_text(json.dumps(data))
    with pytest.raises(ValueError), _adapter()(singlet):
        pytest.fail("invalid native model opened")


@pytest.mark.parametrize("extra", ["CURV 0.01 1", "DIAM NaN", "GLAS MIRROR 0 0"])
def test_zemax_optical_flags_and_nonfinite_apertures_are_rejected(tmp_path, extra):
    from _lib.optiland_backend import validate_zemax
    path = tmp_path / "flagged.zmx"
    path.write_text(ZMX.replace("CURV -0.02", extra if extra.startswith("CURV") else "CURV -0.02\n" + extra))
    with pytest.raises(ValueError):
        validate_zemax(path)


@pytest.mark.tier1
def test_lost_rays_do_not_masquerade_as_improved_spot(singlet):
    from optiland.physical_apertures import EllipticalAperture
    with _adapter()(singlet) as backend:
        backend.lens.surfaces[1].aperture = EllipticalAperture(0.2, 0.2)
        row = backend.evaluate(_spec())[-1]
        assert row["value"] is None
        assert "ray" in row["reason"]


@pytest.mark.tier1
def test_global_metrics_use_and_report_model_primary_wavelength(singlet):
    from optiland.materials import MatchPolicy, Material
    data = json.loads(singlet.read_text())
    data["surface_group"]["surfaces"][1]["material_post"] = Material(
        "N-BK7", catalog="schott", match_policy=MatchPolicy.STRICT).to_dict()
    data["wavelengths"]["wavelengths"][0]["is_primary"] = False
    data["wavelengths"]["wavelengths"][1]["is_primary"] = True
    singlet.write_text(json.dumps(data))
    with _adapter()(singlet) as backend:
        rows = backend.evaluate(_spec())
    # SCHOTT N-BK7 Sellmeier index at 650 nm, then independent thick-lens power.
    n650 = 1.5145203085647796
    expected_efl = 1 / ((n650 - 1) * (0.04 - (n650 - 1) * 5 / (n650 * 2500)))
    assert rows[0]["value"] == pytest.approx(expected_efl, rel=1e-10)
    assert rows[1]["value"] == pytest.approx(expected_efl / 2, rel=1e-10)
    for row in rows[:2]:
        assert row["analysis"]["wavelength"] == 2
        assert row["analysis"]["wavelength_um"] == 0.65


@pytest.mark.tier1
@pytest.mark.parametrize("job", ["audit", "tolerance"])
def test_restricted_zemax_jobs_restore_baseline_and_preserve_ingestion_metadata(tmp_path, job):
    pytest.importorskip("optiland")
    from _lib.design_jobs import run_job
    from _lib.tolerancing import run_tolerance_job
    source = tmp_path / "source.zmx"
    source.write_text(ZMX)
    original = source.read_bytes()
    spec = _spec([{"id": "efl", "metric": "efl_mm", "unit": "mm", "min": 40, "max": 60}])
    out = tmp_path / "job"
    if job == "audit":
        report = run_job(source, spec, out, _adapter())
        assert report["status"] == "requirements_met"
        assert report["baseline"]["inspection"]["import_restrictions"]["format"] == "Zemax sequential text"
    else:
        config = {"schema": "1", "samples": 2, "seed": 3, "sensitivity_steps": [0],
                  "perturbations": [{"surface": 1, "parameter": "radius_mm",
                                     "distribution": "uniform", "half_width_mm": 0.01}]}
        report = run_tolerance_job(source, spec, out, _adapter(), config)
        assert report["status"] == "completed"
        assert report["yield"]["analysis_failures"] == 0
    assert report["baseline_restored"] is True
    assert report["source_unchanged"] is True
    assert source.read_bytes() == original


def test_zemax_explicit_semi_diameter_is_not_silently_discarded(tmp_path):
    from _lib.optiland_backend import validate_zemax
    path = tmp_path / "apertured.zmx"
    path.write_text(ZMX.replace("CURV -0.02", "CURV -0.02\nDIAM 0.1"))
    with pytest.raises(ValueError, match="unsupported Zemax directive: DIAM"):
        validate_zemax(path)


@pytest.mark.parametrize("catalog", ["", "GCAT SCHOTT OHARA\n"])
def test_zemax_glass_requires_one_explicit_catalog(tmp_path, catalog):
    from _lib.optiland_backend import validate_zemax
    path = tmp_path / "catalog.zmx"
    path.write_text(ZMX.replace("GCAT SCHOTT\n", catalog))
    with pytest.raises(ValueError, match="catalog"):
        validate_zemax(path)


@pytest.mark.tier1
def test_zemax_near_spelling_glass_is_rejected(tmp_path):
    pytest.importorskip("optiland")
    path = tmp_path / "misspelled.zmx"
    path.write_text(ZMX.replace("N-BK7", "N-BK77"))
    with pytest.raises(ValueError, match="exact"), _adapter()(path):
        pytest.fail("misspelled glass was accepted")


@pytest.mark.tier1
@pytest.mark.parametrize("change", ["missing_catalog", "near_spelling"])
def test_native_catalog_material_never_uses_fuzzy_resolution(singlet, change):
    from optiland.materials import MatchPolicy, Material
    data = json.loads(singlet.read_text())
    material = Material("N-BK7", catalog="schott", match_policy=MatchPolicy.STRICT).to_dict()
    material["match_policy"] = "best"
    if change == "missing_catalog":
        material["catalog"] = None
    else:
        material["name"] = "N-BK77"
    data["surface_group"]["surfaces"][1]["material_post"] = material
    singlet.write_text(json.dumps(data))
    with pytest.raises(ValueError), _adapter()(singlet):
        pytest.fail("fuzzy or unscoped native material was accepted")


@pytest.mark.tier1
def test_zemax_exact_glass_indices_verified_at_every_wavelength_and_reload(tmp_path):
    pytest.importorskip("optiland")
    path = tmp_path / "two-wavelengths.zmx"
    path.write_text(ZMX.replace("FTYP 0 0 1 1 0 0 0", "FTYP 0 0 1 2 0 0 0")
                   .replace("PWAV 1", "WAVM 2 0.65 1\nPWAV 1"))
    with _adapter()(path) as backend:
        before = backend.inspect()
        glass = before["import_restrictions"]["resolved_glasses"][0]
        assert glass["surface"] == 1 and glass["catalog"] == "schott" and glass["name"] == "N-BK7"
        assert glass["indices"] == [
            {"wavelength_um": 0.55, "index": pytest.approx(1.5185223876207927, rel=1e-12)},
            {"wavelength_um": 0.65, "index": pytest.approx(1.5145203085647796, rel=1e-12)}]
        saved = tmp_path / "saved.json"
        backend.save(saved)
        backend.load(saved)
        assert backend.inspect() == before


@pytest.mark.tier1
def test_converter_material_mismatch_is_recorded_and_replaced_with_exact_glass(tmp_path, monkeypatch):
    pytest.importorskip("optiland")
    from optiland import fileio
    from optiland.materials import IdealMaterial
    convert = fileio.load_zemax_file

    def wrong_converter(path):
        lens = convert(path)
        lens.updater.set_material(IdealMaterial(n=1.7, k=0), 1)
        return lens

    monkeypatch.setattr(fileio, "load_zemax_file", wrong_converter)
    path = tmp_path / "source.zmx"
    path.write_text(ZMX)
    with _adapter()(path) as backend:
        glass = backend.inspect()["import_restrictions"]["resolved_glasses"][0]
        assert glass["converter_indices_matched"] is False
        assert backend.evaluate(_spec())[0]["value"] == pytest.approx(49.05139286997028, rel=1e-10)
