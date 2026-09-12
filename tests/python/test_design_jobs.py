import json
from pathlib import Path

import pytest
from _lib.design_contract import DesignSpec
from _lib.design_jobs import run_job
from test_design_contract import base_spec


class AnalyticFocus:
    """External engine substitute: known physical-style optimum at 47.5 mm.

    Real job runner, files, spec evaluation, search, and acceptance are exercised.
    """
    def __init__(self, model, fail_at=None):
        self.focus = float(Path(model).read_text())
        self.calls = 0
        self.closed = False
        self.fail_at = fail_at

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.closed = True

    def inspect(self):
        return {"engine": {"name": "analytic-test", "version": "1"},
                "focus_mm": self.focus, "invariants": {"efl_mm": 50, "aperture_mm": 10}}

    def set_focus(self, value):
        self.focus = value

    def evaluate(self, spec):
        self.calls += 1
        if self.calls == self.fail_at:
            raise RuntimeError("analysis interrupted")
        return [{"metric": "mtf", "field": 1, "wavelength": 1, "frequency": 50,
                 "axis": "tangential", "unit": "1",
                 "value": 0.9 / (1 + (self.focus - 47.5) ** 2)}]

    def save(self, path):
        Path(path).write_text(str(self.focus))

    def load(self, path):
        self.focus = float(Path(path).read_text())


def test_refocus_preserves_source_and_verifies_saved_candidate(tmp_path):
    model = tmp_path / "source.lens"
    model.write_text("60")
    instances = []
    def factory(path):
        b = AnalyticFocus(path)
        instances.append(b)
        return b
    report = run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / "result", factory,
                     action="refocus")
    assert model.read_text() == "60"
    assert report["status"] == "improved"
    assert report["candidate"]["assessment"]["passes"]
    assert abs(report["candidate"]["inspection"]["focus_mm"] - 47.5) < 0.2
    assert Path(report["artifacts"]["candidate_model"]).exists()
    assert instances[0].closed
    assert report["saved_candidate_verified"]
    assert report["source_unchanged"]


def test_engine_failure_closes_owned_session_and_retains_baseline(tmp_path):
    model = tmp_path / "source.lens"
    model.write_text("60")
    instances = []
    def factory(path):
        b = AnalyticFocus(path, fail_at=3)
        instances.append(b)
        return b
    with pytest.raises(RuntimeError, match="analysis interrupted"):
        run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / "result", factory,
                action="refocus")
    assert instances[0].closed
    assert instances[0].focus == 60
    assert model.read_text() == "60"
    failure = json.loads((tmp_path / "result" / "failure.json").read_text())
    assert failure["baseline_restored"]


def test_output_directory_cannot_overwrite_existing_artifacts(tmp_path):
    model = tmp_path / "source.lens"
    model.write_text("60")
    out = tmp_path / "occupied"
    out.mkdir()
    (out / "keep.txt").write_text("keep")
    with pytest.raises(ValueError):
        run_job(model, DesignSpec.from_dict(base_spec()), out, AnalyticFocus, action="audit")
    assert (out / "keep.txt").read_text() == "keep"


def test_unknown_required_metric_prevents_candidate_acceptance(tmp_path):
    model = tmp_path / "source.lens"
    model.write_text("60")
    data = base_spec()
    data["requirements"].append({"id": "length", "metric": "total_track_mm", "unit": "mm", "max": 70})
    report = run_job(model, DesignSpec.from_dict(data), tmp_path / "result", AnalyticFocus,
                     action="refocus")
    assert report["status"] == "no_acceptable_improvement"
    assert report["artifacts"].get("candidate_model") is None


def test_setup_save_failure_writes_failure_evidence(tmp_path):
    class FailingSave(AnalyticFocus):
        def save(self, path):
            raise RuntimeError('disk failure')
    model = tmp_path / 'lens.txt'
    model.write_text('60')
    with pytest.raises(RuntimeError, match='disk failure'):
        run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'result', FailingSave)
    assert (tmp_path / 'result/failure.json').exists()


def test_saved_candidate_outside_focus_bounds_rejected(tmp_path):
    class BadReload(AnalyticFocus):
        def load(self, path):
            super().load(path)
            if Path(path).name.startswith('candidate'):
                self.focus = 60
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            rows[0]['value'] = .5 if self.calls == 1 else .9
            return rows
    model = tmp_path / 'lens.txt'
    model.write_text('60')
    with pytest.raises(RuntimeError, match='outside'):
        run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'result', BadReload, action='refocus')
    assert json.loads((tmp_path / 'result/failure.json').read_text())['baseline_restored']


def test_native_output_extension_is_independent_of_import_extension(tmp_path):
    class Converted(AnalyticFocus):
        model_suffix = '.json'
    model = tmp_path / 'source.zmx'
    model.write_text('60')
    report = run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'result', Converted)
    assert report['artifacts']['baseline_model'].endswith('.json')


def test_cancelled_job_restores_baseline_and_closes(tmp_path):
    model = tmp_path / 'lens.txt'
    model.write_text('60')
    backend = AnalyticFocus(model)
    with pytest.raises(InterruptedError):
        run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'result', lambda _: backend,
                action='refocus', cancelled=lambda: True)
    assert backend.closed and backend.focus == 60
    assert json.loads((tmp_path / 'result/failure.json').read_text())['baseline_restored']


def test_late_native_result_cannot_pass_after_deadline(tmp_path, monkeypatch):
    import _lib.design_jobs as jobs
    clock = [0]
    monkeypatch.setattr(jobs.time, 'monotonic', lambda: clock[0])
    class Slow(AnalyticFocus):
        def evaluate(self, spec):
            clock[0] += 2
            return super().evaluate(spec)
    model = tmp_path / 'lens.txt'
    model.write_text('60')
    raw = base_spec()
    raw['budget']['timeout_s'] = 1
    with pytest.raises(TimeoutError):
        run_job(model, DesignSpec.from_dict(raw), tmp_path / 'result', Slow)
    assert not (tmp_path / 'result/report.json').exists()


def test_teardown_failure_invalidates_success_receipt(tmp_path):
    class BadClose(AnalyticFocus):
        def __exit__(self, *args):
            raise RuntimeError('engine close failed')
    model = tmp_path / 'lens.txt'
    model.write_text('47.5')
    with pytest.raises(RuntimeError, match='close failed'):
        run_job(model, DesignSpec.from_dict(base_spec()), tmp_path / 'result', BadClose)
    report = json.loads((tmp_path / 'result/report.json').read_text())
    assert report['status'] == 'failed'
    assert (tmp_path / 'result/failure.json').exists()


def test_saved_gain_must_remain_positive_even_within_reload_tolerance(tmp_path):
    class Marginal(AnalyticFocus):
        def __init__(self, model):
            super().__init__(model)
            self.reloaded = False
        def load(self, path):
            super().load(path)
            self.reloaded = Path(path).name.startswith('candidate')
        def evaluate(self, spec):
            rows = super().evaluate(spec)
            rows[0]['value'] = .5 if self.calls == 1 or self.reloaded else .500000001
            return rows
    model = tmp_path / 'lens.txt'
    model.write_text('60')
    raw = base_spec()
    raw['minimum_gain'] = 0
    with pytest.raises(RuntimeError, match='minimum improvement'):
        run_job(model, DesignSpec.from_dict(raw), tmp_path / 'result', Marginal, action='refocus')
