"""Deterministic tolerance workflow against an independently specified affine model."""
import copy
import json
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec


class AffineBackend:
    def __init__(self, path, *, reject_negative_delta=False, fail_save=False):
        self.path = Path(path)
        self.closed = False
        self.loads = 0
        self.reject_negative_delta = reject_negative_delta
        self.fail_save = fail_save
        self.load(path)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def inspect(self):
        return {"engine": "analytic affine fixture", "image_surface": 2,
                "surfaces": [{"index": 1, "radius_mm": self.state["radius_mm"],
                              "thickness_mm": self.state["thickness_mm"]},
                             {"index": 2, "is_image": True}],
                "invariants": {"surface_count": 3}}

    def evaluate(self, _spec):
        return [{"metric": "efl_mm", "unit": "mm",
                 "value": self.state["radius_mm"] + 2 * (self.state["thickness_mm"] - 2)}]

    def save(self, path):
        if self.fail_save:
            raise OSError("synthetic save failure")
        Path(path).write_text(json.dumps(self.state), encoding="utf-8")

    def load(self, path):
        self.loads += 1
        self.state = json.loads(Path(path).read_text(encoding="utf-8"))

    def get_parameter(self, surface, name):
        if surface != 1:
            raise ValueError("object/image surfaces cannot be perturbed")
        return self.state[name]

    def set_parameter(self, surface, name, value):
        self.get_parameter(surface, name)
        if self.reject_negative_delta and name == "radius_mm" and value < 10:
            raise ValueError("synthetic invalid prescription")
        self.state[name] = value


@pytest.fixture
def tolerance_setup(tmp_path):
    source = tmp_path / "source.json"
    source.write_text('{"radius_mm":10,"thickness_mm":2}', encoding="utf-8")
    spec = DesignSpec.from_dict({"schema": "1", "fields": [1], "wavelengths": [1],
                                "requirements": [{"id": "efl", "metric": "efl_mm", "unit": "mm", "min": 9.5, "max": 10.5}]})
    config = {"schema": "1", "samples": 5, "seed": 0,
              "perturbations": [{"surface": 1, "parameter": "radius_mm", "distribution": "uniform", "half_width_mm": 1}]}
    backends = []

    def factory(path):
        backend = AffineBackend(path)
        backends.append(backend)
        return backend

    return source, spec, config, factory, backends


def test_sensitivity_and_seeded_yield_restore_each_trial(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, factory, backends = tolerance_setup
    original = source.read_bytes()
    out = tmp_path / "run"
    report = run_tolerance_job(source, spec, out, factory, config)
    assert report["nominal"]["assessment"]["passes"] is True
    assert [r["measurements"][0]["value"] for r in report["sensitivity"]] == [9, 10, 11]
    assert [r["assessment"]["passes"] for r in report["sensitivity"]] == [False, True, False]
    trials = report["monte_carlo"]
    # First five Python MT19937 uniform(-1,1) variates with seed 0, fixed independently.
    expected = [.6888437030500962, .515908805880605, -.15885683833831, -.4821664994140733, .02254944273721704]
    assert [r["perturbations"][0]["delta_mm"] for r in trials] == pytest.approx(expected)
    assert [r["measurements"][0]["value"] for r in trials] == pytest.approx([10 + v for v in expected])
    assert report["yield"]["passes"] == 3
    assert report["yield"]["failures"] == 2
    assert report["yield"]["fraction"] == .6
    assert report["yield"]["wilson_95"] == pytest.approx([.2307242813, .8823792258])
    assert report["compensation"] == "none"
    assert report["source_unchanged"] is True and source.read_bytes() == original
    assert backends[0].state == {"radius_mm": 10, "thickness_mm": 2}
    assert backends[0].closed and backends[0].path != source
    assert json.loads((out / "report.json").read_text())["yield"]["fraction"] == .6


def test_invalid_prescriptions_count_against_yield_and_recover(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    backends = []

    def factory(path):
        backend = AffineBackend(path, reject_negative_delta=True)
        backends.append(backend)
        return backend

    report = run_tolerance_job(source, spec, tmp_path / "run", factory, config)
    assert report["yield"]["passes"] == 1
    assert report["yield"]["failures"] == 4
    assert report["yield"]["analysis_failures"] == 2
    errors = [r for r in report["monte_carlo"] if r["status"] == "analysis_failed"]
    assert len(errors) == 2 and all("invalid prescription" in r["error"] for r in errors)
    assert backends[0].state["radius_mm"] == 10 and backends[0].closed


@pytest.mark.parametrize("change", [
    {"compensators": []}, {"samples": 0}, {"samples": 1001}, {"samples": True},
    {"seed": None}, {"seed": .5}, {"timeout_s": 0}, {"timeout_s": float("inf")},
    {"sensitivity_steps": []}, {"sensitivity_steps": [float("nan")]},
    {"perturbations": [{"surface": 0, "parameter": "radius_mm", "distribution": "uniform", "half_width_mm": 1}]},
    {"perturbations": [{"surface": 1, "parameter": "refractive_index", "distribution": "uniform", "half_width_mm": 1}]},
    {"perturbations": [{"surface": 1, "parameter": "radius_mm", "distribution": "normal", "half_width_mm": 1}]},
    {"perturbations": [{"surface": 1, "parameter": "radius_mm", "distribution": "uniform", "half_width_mm": -1}]},
])
def test_invalid_tolerance_contract_never_opens_engine(tolerance_setup, tmp_path, change):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, factory, backends = tolerance_setup
    with pytest.raises(ValueError):
        run_tolerance_job(source, spec, tmp_path / "run", factory, {**config, **change})
    assert backends == []


def test_existing_output_is_immutable(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, factory, backends = tolerance_setup
    out = tmp_path / "run"
    out.mkdir()
    (out / "keep.txt").write_text("keep")
    with pytest.raises(ValueError):
        run_tolerance_job(source, spec, out, factory, config)
    assert (out / "keep.txt").read_text() == "keep" and backends == []


def test_setup_failure_closes_backend_and_writes_failure(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    backends = []

    def factory(path):
        b = AffineBackend(path, fail_save=True)
        backends.append(b)
        return b

    out = tmp_path / "run"
    with pytest.raises(OSError, match="save failure"):
        run_tolerance_job(source, spec, out, factory, config)
    assert backends[0].closed
    failure = json.loads((out / "failure.json").read_text())
    assert failure["source_unchanged"] is True and failure["error_type"] == "OSError"


def test_normal_sampling_repeatable_and_inputs_unmodified(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, factory, _ = tolerance_setup
    config["perturbations"] = [{"surface": 1, "parameter": "thickness_mm", "distribution": "normal", "sigma_mm": .25}]
    before = copy.deepcopy(config)
    a = run_tolerance_job(source, spec, tmp_path / "a", factory, config)
    b = run_tolerance_job(source, spec, tmp_path / "b", factory, config)
    assert a["monte_carlo"] == b["monte_carlo"] and config == before
    assert [r["measurements"][0]["value"] for r in a["sensitivity"]] == [9.5, 10, 10.5]


def test_failed_trial_keeps_all_requested_deltas(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    config["perturbations"].append({"surface": 1, "parameter": "thickness_mm", "distribution": "uniform", "half_width_mm": .1})
    report = run_tolerance_job(source, spec, tmp_path / "run",
                               lambda p: AffineBackend(p, reject_negative_delta=True), config)
    errors = [r for r in report["monte_carlo"] if r["status"] == "analysis_failed"]
    assert errors and all(len(r["perturbations"]) == 2 for r in errors)


def test_nonfinite_engine_measurement_is_recorded_as_failed_sample(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup

    class BadMeasurement(AffineBackend):
        def evaluate(self, spec):
            result = super().evaluate(spec)
            result[0]["value"] = float("nan")
            return result

    out = tmp_path / "run"
    report = run_tolerance_job(source, spec, out, BadMeasurement, config)
    assert report["yield"]["analysis_failures"] == 5 and report["yield"]["fraction"] == 0
    assert report["monte_carlo"][0]["measurements"][0]["value"] == "nan"
    assert "finite" in report["monte_carlo"][0]["error"]
    assert json.loads((out / "report.json").read_text())["yield"]["failures"] == 5


def test_timeout_writes_incomplete_evidence_restores_and_closes(tolerance_setup, tmp_path, monkeypatch):
    from _lib import tolerancing

    source, spec, config, _, _ = tolerance_setup
    clock, backends = [0], []
    monkeypatch.setattr(tolerancing.time, "monotonic", lambda: clock[0])

    class SlowBackend(AffineBackend):
        def evaluate(self, spec):
            clock[0] += 1000
            return super().evaluate(spec)

    def factory(path):
        backend = SlowBackend(path)
        backends.append(backend)
        return backend

    out = tmp_path / "run"
    with pytest.raises(TimeoutError):
        tolerancing.run_tolerance_job(source, spec, out, factory, config)
    failure = json.loads((out / "failure.json").read_text())
    assert failure["yield"]["not_run"] == 5 and failure["yield"]["fraction"] is None
    assert failure["baseline_restored"] and backends[0].closed
    assert backends[0].state == {"radius_mm": 10, "thickness_mm": 2}


def test_image_surface_rejected_without_any_trials(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, factory, backends = tolerance_setup
    config["perturbations"][0]["surface"] = 2
    out = tmp_path / "run"
    with pytest.raises(ValueError, match="image surface"):
        run_tolerance_job(source, spec, out, factory, config)
    assert json.loads((out / "failure.json").read_text())["evaluations"] == 0
    assert backends[0].closed


def test_factory_failure_has_failure_artifact(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup

    def factory(_path):
        raise RuntimeError("license unavailable")

    out = tmp_path / "run"
    with pytest.raises(RuntimeError, match="license"):
        run_tolerance_job(source, spec, out, factory, config)
    assert json.loads((out / "failure.json").read_text())["source_unchanged"] is True


def test_baseline_uses_backend_native_extension_after_import(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    imported = source.with_suffix(".zmx")
    imported.write_bytes(source.read_bytes())

    class JsonBackend(AffineBackend):
        model_suffix = ".json"

        def save(self, path):
            if Path(path).suffix != ".json":
                raise ValueError("backend only saves native JSON")
            super().save(path)

    report = run_tolerance_job(imported, spec, tmp_path / "run", JsonBackend, config)
    assert Path(report["artifacts"]["baseline_model"]).suffix == ".json"
    assert report["baseline_restored"] is True


def test_noop_setter_cannot_report_yield_for_unapplied_changes(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup

    class NoopSetter(AffineBackend):
        def set_parameter(self, surface, name, value):
            pass

    report = run_tolerance_job(source, spec, tmp_path / "run", NoopSetter, config)
    assert report["yield"]["fraction"] == 0
    assert report["yield"]["analysis_failures"] == 5
    assert all(not r["perturbations"][0]["applied"] for r in report["monte_carlo"])
    assert all(r["perturbations"][0]["readback_mm"] == 10 for r in report["monte_carlo"])


def test_readback_happens_after_all_edits(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    config["perturbations"].append({"surface": 1, "parameter": "thickness_mm", "distribution": "uniform", "half_width_mm": .1})

    class CoupledSetter(AffineBackend):
        def set_parameter(self, surface, name, value):
            super().set_parameter(surface, name, value)
            if name == "thickness_mm":
                self.state["radius_mm"] = 10

    report = run_tolerance_job(source, spec, tmp_path / "run", CoupledSetter, config)
    assert report["yield"]["analysis_failures"] == 5
    for row in report["monte_carlo"]:
        assert row["perturbations"][0]["applied"] is False
        assert row["perturbations"][1]["applied"] is True


def test_silent_load_failure_is_detected_before_next_trial(tolerance_setup, tmp_path):
    from _lib.tolerancing import run_tolerance_job

    source, spec, config, _, _ = tolerance_setup
    instances = []

    class NoopRestore(AffineBackend):
        def load(self, path):
            if self.loads >= 3:
                return
            super().load(path)

    def factory(path):
        backend = NoopRestore(path)
        instances.append(backend)
        return backend

    out = tmp_path / "run"
    with pytest.raises(RuntimeError, match="baseline.*before trial"):
        run_tolerance_job(source, spec, out, factory, config)
    failure = json.loads((out / "failure.json").read_text())
    assert failure["evaluations"] == 2  # nominal and first sensitivity, then stop
    assert failure["yield"]["attempted"] == 0 and instances[0].closed
