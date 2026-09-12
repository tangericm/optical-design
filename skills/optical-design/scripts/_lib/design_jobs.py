"""Copy-on-write optical jobs with bounded search and verifiable evidence."""
from __future__ import annotations

import hashlib
import json
import math
import platform
import shutil
import time
from pathlib import Path

from _lib.design_contract import DesignSpec, assess, objective_value


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")


def write_report(path, report):
    lines = ["# Optical design review", "", f"Outcome: **{report['status']}**.", "",
             f"Source: `{report['source']['path']}`", "",
             f"Source SHA-256: `{report['source']['sha256']}`", "",
             "Only the final image-space gap may change during refocus. All declared requirements are hard constraints.", ""]
    for name in ("baseline", "candidate"):
        entry = report.get(name)
        if entry is None:
            continue
        lines += [f"## {name.title()}", "", f"Image distance: {entry['inspection']['focus_mm']:.8g} mm.", "",
                  "| Requirement | Status | Value | Unit |", "|---|---|---|---|"]
        for r in entry["assessment"]["requirements"]:
            lines.append(f"| {r['id']} | {r['status']} | {r.get('value', r.get('reason', ''))} | {r.get('unit', '')} |")
        lines += [""]
    lines += ["## Evidence", "", f"Evaluations: {report['evaluations']}. Source unchanged: {report['source_unchanged']}.", "",
              "Full metrics, analysis settings, engine version, search history, and artifact hashes are in report.json.", "",
              "The time budget is checked between native analysis calls. A blocking engine call can exceed it.", "",
              "Refocus searches one bounded gap; it does not perform a general lens redesign or certify manufacturing yield.", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def run_job(model, spec: DesignSpec, out, factory, *, action="audit", cancelled=None) -> dict:
    """Ensure setup/teardown errors also leave failure evidence without accepting a result."""
    target = Path(out).resolve()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError('output directory must be new or empty; existing artifacts are never overwritten')
    try:
        return _run_job(model, spec, out, factory, action=action, cancelled=cancelled)
    except BaseException as exc:
        if target.is_dir():
            failure = target / 'failure.json'
            if not failure.exists():
                write_json(failure, {'error': str(exc), 'error_type': type(exc).__name__,
                                    'baseline_restored': False, 'stage': 'setup_or_teardown'})
            # A report is not a success receipt if engine teardown failed.
            report_path = target / 'report.json'
            if report_path.exists():
                prior = json.loads(report_path.read_text(encoding='utf-8'))
                prior['status'] = 'failed'
                prior['saved_candidate_verified'] = False
                prior['error'] = str(exc)
                write_json(report_path, prior)
                write_report(target / 'report.md', prior)
        raise


def _run_job(model, spec: DesignSpec, out, factory, *, action="audit", cancelled=None) -> dict:
    if action not in {"audit", "refocus"}:
        raise ValueError("action must be audit or refocus")
    if action == "refocus" and (spec.objective is None or "focus" not in spec.data):
        raise ValueError("refocus requires objective and explicit focus bounds")
    model, out = Path(model).resolve(strict=True), Path(out).resolve()
    if not model.is_file():
        raise ValueError("model must be a file")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("output directory must be new or empty; existing artifacts are never overwritten")
    out.mkdir(parents=True, exist_ok=True)
    original_hash = sha256(model)
    working = out / ("working" + model.suffix)
    baseline_path = out / ("baseline-model" + model.suffix)
    candidate_path = out / ("candidate-model" + model.suffix)
    shutil.copy2(model, working)
    write_json(out / "spec.json", spec.data)
    deadline = time.monotonic() + spec.data["budget"]["timeout_s"]
    count, history = 0, []
    baseline = None

    def check_budget():
        if cancelled and cancelled():
            raise InterruptedError("job cancelled")
        if time.monotonic() > deadline:
            raise TimeoutError("job time budget exhausted between native calls")
        if count >= spec.data["budget"]["max_evaluations"]:
            raise RuntimeError("evaluation budget exhausted")

    with factory(working) as backend:
        suffix = getattr(backend, 'model_suffix', model.suffix)
        baseline_path = out / ('baseline-model' + suffix)
        candidate_path = out / ('candidate-model' + suffix)
        initial = backend.inspect()
        backend.save(baseline_path)

        def evaluate():
            nonlocal count
            check_budget()
            rows = backend.evaluate(spec)
            count += 1
            if time.monotonic() > deadline or (cancelled and cancelled()):
                raise TimeoutError('job cancelled or time budget exhausted after native call')
            inspection = backend.inspect()
            if inspection["invariants"] != initial["invariants"]:
                raise RuntimeError("optical model invariants changed outside the allowed focus gap")
            result = {"inspection": inspection, "measurements": rows, "assessment": assess(spec, rows)}
            history.append({"focus_mm": inspection["focus_mm"], "assessment": result["assessment"],
                            "measurements": rows})
            return result

        try:
            baseline = evaluate()
            write_json(out / "baseline.json", baseline)
            candidate = None
            if action == "refocus":
                sign = 1 if spec.objective["direction"] == "maximize" else -1
                base_value = objective_value(spec, baseline["measurements"])
                best, best_score = None, -math.inf
                lo, hi = spec.data["focus"]["min_mm"], spec.data["focus"]["max_mm"]
                # Reserve two evaluations for best-candidate verification and saved/reloaded verification.
                search_budget = spec.data["budget"]["max_evaluations"] - 3
                coarse_count = min(7, search_budget)
                points = [lo + i * (hi - lo) / (coarse_count - 1) for i in range(coarse_count)]
                samples = []

                def sample(position):
                    nonlocal best, best_score
                    backend.set_focus(position)
                    result = evaluate()
                    score = sign * objective_value(spec, result["measurements"])
                    samples.append((position, score))
                    if result["assessment"]["passes"] and score > best_score:
                        best, best_score = result, score
                    return score

                for point in points:
                    sample(point)
                peak = max(samples, key=lambda p: p[1])[0]
                step = (hi - lo) / (coarse_count - 1)
                left, right = max(lo, peak - step), min(hi, peak + step)
                # Refine within the best coarse interval; this is a bounded local search, not a global proof.
                ratio = (math.sqrt(5) - 1) / 2
                while len(samples) + 2 <= search_budget:
                    x1, x2 = right - ratio * (right - left), left + ratio * (right - left)
                    y1, y2 = sample(x1), sample(x2)
                    if y1 > y2:
                        right = x2
                    else:
                        left = x1
                if best and best_score - sign * base_value > spec.data["minimum_gain"]:
                    backend.set_focus(best["inspection"]["focus_mm"])
                    candidate = evaluate()
                    if (not candidate["assessment"]["passes"] or
                            sign * (objective_value(spec, candidate["measurements"]) - base_value) <= spec.data["minimum_gain"]):
                        raise RuntimeError("candidate improvement did not reproduce")
                    backend.save(candidate_path)
                    backend.load(candidate_path)
                    reloaded = evaluate()
                    if not reloaded["assessment"]["passes"]:
                        raise RuntimeError("saved candidate violates requirements on reload")
                    before = objective_value(spec, candidate["measurements"])
                    after = objective_value(spec, reloaded["measurements"])
                    if not math.isclose(before, after, rel_tol=1e-5, abs_tol=1e-8):
                        raise RuntimeError("saved candidate objective changed on reload")
                    if sign * (after - base_value) <= spec.data['minimum_gain']:
                        raise RuntimeError('saved candidate no longer exceeds minimum improvement')
                    if not lo <= reloaded['inspection']['focus_mm'] <= hi:
                        raise RuntimeError('saved candidate focus lies outside allowed bounds')
                    candidate = reloaded
                else:
                    candidate = None
            source_unchanged = sha256(model) == original_hash
            if not source_unchanged:
                raise RuntimeError("source changed during job; results cannot be accepted")
            backend.load(baseline_path)
            if backend.inspect() != initial:
                raise RuntimeError('baseline restoration did not reproduce the original inspection')
            status = ("improved" if candidate else "no_acceptable_improvement") if action == "refocus" else (
                "requirements_met" if baseline["assessment"]["passes"] else "requirements_not_met")
            artifacts = {"baseline_model": str(baseline_path), "baseline_sha256": sha256(baseline_path)}
            if candidate:
                artifacts.update(candidate_model=str(candidate_path), candidate_sha256=sha256(candidate_path))
            report = {"schema": "1", "action": action, "status": status,
                      "source": {"path": str(model), "sha256": original_hash}, "spec": spec.data,
                      "python_version": platform.python_version(), "baseline": baseline, "candidate": candidate,
                      "history": history, "evaluations": count, "source_unchanged": source_unchanged,
                      "saved_candidate_verified": candidate is not None, "artifacts": artifacts,
                      "baseline_restored": True, "spec_sha256": sha256(out / 'spec.json'),
                      "time_budget_policy": "cooperative_between_native_calls"}
            write_json(out / "report.json", report)
            write_report(out / "report.md", report)
            return report
        except BaseException as exc:
            restored = False
            restoration_error = None
            try:
                backend.load(baseline_path)
                restored = backend.inspect() == initial
            except Exception as restore_exc:  # noqa: BLE001 -- retain original engine failure and cleanup evidence
                restoration_error = str(restore_exc)
            write_json(out / "failure.json", {"error": str(exc), "error_type": type(exc).__name__,
                       "restoration_error": restoration_error,
                       "baseline_restored": restored, "source_unchanged": sha256(model) == original_hash,
                       "evaluations": count, "history": history})
            raise
