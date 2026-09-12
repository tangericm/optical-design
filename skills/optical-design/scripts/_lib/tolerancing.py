"""Seeded, uncompensated tolerance trials on disposable native model copies."""
from __future__ import annotations

import copy
import math
import platform
import random
import shutil
import time
from pathlib import Path

from _lib.design_contract import DesignSpec, assess, finite
from _lib.design_jobs import sha256, write_json


def _validate(raw: dict, spec: DesignSpec) -> dict:
    if not isinstance(raw, dict) or raw.get("schema") != "1":
        raise ValueError("tolerance specification requires schema '1'")
    allowed = {"schema", "perturbations", "samples", "seed", "sensitivity_steps", "timeout_s"}
    if set(raw) - allowed:
        raise ValueError(f"unsupported tolerance keys (compensation is not supported): {sorted(set(raw) - allowed)}")
    config = copy.deepcopy(raw)
    if type(config.get("samples")) is not int or not 1 <= config["samples"] <= 1000:
        raise ValueError("samples must be an integer from 1 through 1000")
    if type(config.get("seed")) is not int:
        raise ValueError("seed must be an explicit integer")
    config.setdefault("timeout_s", spec.data["budget"]["timeout_s"])
    if finite(config["timeout_s"], "timeout_s") <= 0:
        raise ValueError("timeout_s must be positive")
    steps = config.setdefault("sensitivity_steps", [-1, 0, 1])
    if not isinstance(steps, list) or not 1 <= len(steps) <= 21:
        raise ValueError("sensitivity_steps requires 1 through 21 finite scale factors")
    for step in steps:
        finite(step, "sensitivity step")
    perturbations = config.get("perturbations")
    if not isinstance(perturbations, list) or not 1 <= len(perturbations) <= 32:
        raise ValueError("perturbations requires 1 through 32 independent parameters")
    seen = set()
    for p in perturbations:
        if not isinstance(p, dict):
            raise ValueError("each perturbation must be an object")  # noqa: TRY004 -- CLI contract errors use exit 2.
        distribution = p.get("distribution")
        width = {"uniform": "half_width_mm", "normal": "sigma_mm"}.get(distribution)
        if width is None or set(p) != {"surface", "parameter", "distribution", width}:
            raise ValueError("use uniform with half_width_mm, or normal with sigma_mm; extra perturbation keys are unsupported")
        if type(p["surface"]) is not int or p["surface"] < 1:
            raise ValueError("surface must be a positive native surface index; object/image surfaces are excluded")
        if p["parameter"] not in {"radius_mm", "thickness_mm"}:
            raise ValueError("only radius_mm and thickness_mm perturbations are supported")
        if finite(p[width], width) <= 0:
            raise ValueError(f"{width} must be positive")
        identity = (p["surface"], p["parameter"])
        if identity in seen:
            raise ValueError("duplicate perturbed surface/parameter")
        seen.add(identity)
    return config


def _yield(trials: list[dict], requested: int) -> dict:
    """Wilson score interval for completed independent trials; analysis errors fail."""
    count = len(trials)
    passed = sum(r["status"] == "pass" for r in trials)
    interval = None
    if count:
        z = 1.959963984540054
        fraction = passed / count
        divisor = 1 + z * z / count
        center = (fraction + z * z / (2 * count)) / divisor
        radius = z * math.sqrt(fraction * (1 - fraction) / count + z * z / (4 * count * count)) / divisor
        interval = [max(0.0, center - radius), min(1.0, center + radius)]
    return {"requested": requested, "attempted": count, "not_run": requested - count,
            "passes": passed, "failures": count - passed,
            "analysis_failures": sum(r["status"] == "analysis_failed" for r in trials),
            "fraction": passed / count if count else None, "wilson_95": interval,
            "interval_scope": "completed independent Monte Carlo trials; analysis failures count as failures; no compensation"}


def _failure_evidence(value):
    """Preserve nonfinite engine evidence as explicit strings in strict JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: _failure_evidence(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_failure_evidence(v) for v in value]
    return value


def run_tolerance_job(model, spec: DesignSpec, out, factory, tolerance: dict) -> dict:
    """Restore the native baseline before every sensitivity/Monte Carlo evaluation.

    The factory is a context manager owning a standalone backend on a copied model.
    Parameters use native surface indices. Adapters must reject image/object surfaces
    and physically invalid prescriptions. Sensitivity is one parameter at a time;
    Monte Carlo applies all independent draws together. No compensators are inferred.
    Time limits are cooperative between native calls, never an engine interruption.
    """
    config = _validate(tolerance, spec)
    model, out = Path(model).resolve(strict=True), Path(out).resolve()
    if not model.is_file():
        raise ValueError("model must be a file")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("output directory must be new or empty; existing evidence is immutable")
    original_hash = sha256(model)
    out.mkdir(parents=True, exist_ok=True)
    working = out / ("working" + model.suffix)
    baseline_path = out / ("baseline" + model.suffix)
    original_copy = out / ("source_snapshot" + model.suffix)
    deadline = time.monotonic() + config["timeout_s"]
    sensitivity, monte_carlo = [], []
    nominal, initial = None, None
    restored, cleanup_error = False, None
    evaluations = 0

    def check_time():
        if time.monotonic() >= deadline:
            raise TimeoutError("tolerance time budget exhausted between native calls")

    def call(function, *args):
        check_time()
        value = function(*args)
        check_time()
        return value

    try:
        shutil.copy2(model, working)
        shutil.copy2(model, original_copy)
        write_json(out / "spec.json", spec.data)
        write_json(out / "tolerance.json", config)
        with factory(working) as backend:
            baseline_path = out / ("baseline" + getattr(backend, "model_suffix", model.suffix))
            recovery = original_copy
            active_error = None
            try:
                initial = copy.deepcopy(call(backend.inspect))
                call(backend.save, baseline_path)
                recovery = baseline_path
                base_parameters = []
                for p in config["perturbations"]:
                    if p["surface"] == initial.get("image_surface"):
                        raise ValueError("image surface cannot be perturbed")
                    for surface in initial.get("surfaces", []):
                        if surface.get("index") == p["surface"] and surface.get("is_image"):
                            raise ValueError("image surface cannot be perturbed")
                    value = finite(call(backend.get_parameter, p["surface"], p["parameter"]), "baseline parameter")
                    base_parameters.append({**p, "baseline_mm": value})

                def trial(kind, index, deltas):
                    nonlocal evaluations
                    # Restoration failure is fatal: subsequent trials cannot be trusted.
                    call(backend.load, baseline_path)
                    if call(backend.inspect) != initial:
                        raise RuntimeError("native baseline did not reproduce before trial")
                    entry = {"kind": kind, "index": index, "perturbations": [],
                             "baseline_verified": True,
                             "measurements": [], "assessment": {"passes": False, "requirements": []}}
                    for parameter_index, delta in deltas:
                        p = base_parameters[parameter_index]
                        entry["perturbations"].append({"surface": p["surface"], "parameter": p["parameter"],
                                                       "baseline_mm": p["baseline_mm"], "delta_mm": delta,
                                                       "value_mm": p["baseline_mm"] + delta, "applied": False})
                    try:
                        for p in entry["perturbations"]:
                            value = finite(p["value_mm"], "perturbed parameter")
                            call(backend.set_parameter, p["surface"], p["parameter"], value)
                        mismatches = []
                        # A later edit can change an earlier one through engine coupling.
                        # Verify the complete requested state only after all setters finish.
                        for p in entry["perturbations"]:
                            p["readback_mm"] = call(backend.get_parameter, p["surface"], p["parameter"])
                            actual = finite(p["readback_mm"], "parameter readback")
                            matches = math.isclose(actual, p["value_mm"], rel_tol=1e-12, abs_tol=1e-12)
                            changed = p["delta_mm"] == 0 or actual != p["baseline_mm"]
                            p["applied"] = matches and changed
                            if not p["applied"]:
                                mismatches.append(f"surface {p['surface']} {p['parameter']}")
                        if mismatches:
                            raise RuntimeError(f"edited parameters did not reproduce at readback: {', '.join(mismatches)}")
                        evaluations += 1
                        entry["measurements"] = call(backend.evaluate, spec)
                        entry["assessment"] = assess(spec, entry["measurements"])
                        entry["status"] = "pass" if entry["assessment"]["passes"] else "fail"
                    except (TimeoutError, InterruptedError):
                        raise
                    except Exception as exc:  # noqa: BLE001 -- native failures are preserved as failed trial evidence.
                        entry.update(status="analysis_failed", error=str(exc), error_type=type(exc).__name__)
                        entry = _failure_evidence(entry)
                    return entry

                nominal = trial("nominal", 0, [])
                write_json(out / "nominal.json", nominal)
                for index, p in enumerate(base_parameters):
                    width = p.get("half_width_mm", p.get("sigma_mm"))
                    for step in config["sensitivity_steps"]:
                        delta = finite(step * width, "sensitivity delta")
                        row = trial("sensitivity", len(sensitivity), [(index, delta)])
                        row["scale_factor"] = step
                        sensitivity.append(row)
                        write_json(out / "sensitivity.json", sensitivity)
                rng = random.Random(config["seed"])
                for index in range(config["samples"]):
                    deltas = [(j, rng.uniform(-p["half_width_mm"], p["half_width_mm"]) if p["distribution"] == "uniform"
                               else rng.gauss(0, p["sigma_mm"])) for j, p in enumerate(base_parameters)]
                    monte_carlo.append(trial("monte_carlo", index, deltas))
                    write_json(out / "monte_carlo.json", monte_carlo)
            except BaseException as exc:
                active_error = exc
                raise
            finally:
                # Cleanup is mandatory even after timeout; never gate restoration on the budget.
                try:
                    backend.load(recovery)
                    restored = True
                    if initial is not None:
                        restored = backend.inspect() == initial
                    if not restored:
                        raise RuntimeError("native baseline did not reproduce during cleanup")
                except BaseException as exc:
                    cleanup_error = f"{type(exc).__name__}: {exc}"
                    if active_error is None:
                        raise
        if sha256(model) != original_hash:
            raise RuntimeError("source changed during tolerance job; evidence cannot be accepted")
        report = {"schema": "1", "action": "tolerance", "status": "completed",
                  "source": {"path": str(model), "sha256": original_hash}, "source_unchanged": True,
                  "spec": spec.data, "tolerance": config, "inspection": initial,
                  "nominal": nominal, "sensitivity": sensitivity, "monte_carlo": monte_carlo,
                  "yield": _yield(monte_carlo, config["samples"]), "compensation": "none",
                  "baseline_restored": restored, "evaluations": evaluations,
                  "parameter_readback_tolerance": {"relative": 1e-12, "absolute_mm": 1e-12,
                                                   "nonzero_delta_requires_actual_change": True},
                  "python_version": platform.python_version(), "random_engine": "Python random.Random MT19937; independent uniform or Gaussian draws",
                  "time_budget_policy": "cooperative_between_native_calls",
                  "artifacts": {"baseline_model": str(baseline_path), "baseline_sha256": sha256(baseline_path),
                                "source_snapshot_sha256": sha256(original_copy)}}
        write_json(out / "report.json", report)
        return report
    except BaseException as exc:
        write_json(out / "failure.json", {"schema": "1", "action": "tolerance", "status": "failed",
                   "error": str(exc), "error_type": type(exc).__name__, "cleanup_error": cleanup_error,
                   "baseline_restored": restored, "source_unchanged": model.is_file() and sha256(model) == original_hash,
                   "nominal": nominal, "sensitivity": sensitivity, "monte_carlo": monte_carlo,
                   "evaluations": evaluations, "yield": _yield(monte_carlo, config["samples"])})
        raise
