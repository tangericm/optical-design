"""Paraxial first-order computations on an Optiland Optic model.

Shared by ``first_order.py`` and ``inspect_zmx.py``. Every number here is read
straight out of Optiland's own ``Paraxial`` module (pinned optiland==0.6.2);
nothing in this file re-derives an optics formula, it only assembles
Optiland's building blocks (marginal/chief ray traces, f1/f2/FNO/EPD/XPL/EPL,
the Lagrange invariant) into named, unit-tagged results an agent can gate a
design against before spending an optimization budget on it.

Two Optiland API quirks worth recording, found while writing this module:

- ``Optic.total_track`` is a *property*, not a method (``optic.total_track``,
  no parentheses) -- calling it shadows nothing, but calling it *as* a
  function raises a confusing ``'numpy.float64' object is not callable``.
- ``Paraxial.f2()`` (EFL) always reads ``optic.primary_wavelength`` internally
  and takes no wavelength argument, so a per-wavelength EFL sweep for the
  EFL spread has to redo its trace by hand (see ``_efl_at``
  below) rather than calling ``f2()`` once per wavelength.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

from . import optics
from .import_fidelity import load_assessed_model

# Gate keys accepted by evaluate_gate(); kept in sync with the flat keys compute() emits.
GATE_KEYS = {
    "efl_mm", "bfl_mm", "f_number", "na_image", "epd_mm", "total_track_mm",
    "telecentricity_deg", "chromatic_shift_um", "chief_ray_height_mm",
    "magnification", "lagrange_invariant",
    "image_distance_mm", "back_focal_length_mm", "na_image_paraxial",
    "efl_spread_um", "chief_ray_angle_paraxial_deg",
}


def load_optic(model_path: str) -> Any:
    """Load a ``.zmx`` or Optiland-native ``.json`` model as an optiland Optic.

    Raises ValueError for an unrecognized extension or a prescription Optiland's
    reader itself rejects -- callers should treat that as an analysis failure,
    not a usage error: the arguments were fine, the file wasn't.
    """
    optic, _ = load_assessed_model(model_path)
    return optic


def _scalar(value: Any) -> float:
    """Coerce a Paraxial result to a plain float.

    Most Paraxial methods already return a pre-indexed scalar, but a few (e.g.
    ``EPL()`` when the stop is surface 1) return a bare 0-d array instead, which
    ``float()`` handles directly but ``value[0]`` cannot (0-d arrays are not
    indexable). Try the direct conversion first; fall back to indexing for the
    ordinary 1-element array case.
    """
    try:
        return float(value)
    except TypeError:
        v = value[0]
        return float(v.item() if hasattr(v, "item") else v)


def _finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None


def _efl_at(optic: Any, wavelength_um: float) -> float:
    """Optiland's own ``Paraxial.f2()`` trace, redone at an explicit wavelength.

    ``f2()`` always uses ``optic.primary_wavelength``; this repeats its exact
    formula (unit ray from one lens unit before the first surface) so the
    chromatic sweep below does not have to mutate the optic to change the
    "primary" wavelength.
    """
    p = optic.paraxial
    z_start = p.surfaces.positions[1] - 1
    y, u = p.trace_generic(1.0, 0.0, z_start, wavelength_um)
    return _scalar(-y[0] / u[-1])


def compute(optic: Any) -> dict[str, Any]:
    """First-order summary for ``optic``.

    Returns ``{"results": {...}, "units": {...}, "warnings": [...]}``. ``results``
    is flat (no nesting) so it doubles as the input to ``evaluate_gate``; a value
    that is not finite for this model (e.g. magnification of an afocal system) is
    reported as ``None`` with an accompanying warning rather than raised.
    """
    p = optic.paraxial
    assessment = getattr(optic, "_import_fidelity", None)
    warnings: list[str] = list(assessment["warnings"]) if assessment else []

    efl = p.f2()
    fno = p.FNO()
    epd = p.EPD()
    positions = optic.surfaces.positions
    image_distance = _scalar(positions[-1] - positions[-2])
    # F2 is measured from the image plane, for parallel input rays at primary wavelength.
    bfl = image_distance + _scalar(p.F2())
    total_track = float(optic.total_track)
    invariant = p.invariant()

    wavelengths_um = list(optic.wavelengths.get_wavelengths())
    primary_um = float(optic.primary_wavelength)
    per_wavelength_efl_mm = {f"{w:.6g}": _efl_at(optic, w) for w in wavelengths_um}
    finite_efls = [v for v in per_wavelength_efl_mm.values() if math.isfinite(v)]
    chromatic_shift_um = (max(finite_efls) - min(finite_efls)) * 1000.0 if len(finite_efls) > 1 else 0.0

    y_chief, u_chief = p.chief_ray()
    telecentricity_deg = math.degrees(math.atan(_scalar(u_chief[-1])))
    chief_ray_height_mm = _scalar(y_chief[-1])

    raw: dict[str, float] = {
        "efl_mm": _scalar(efl),
        "bfl_mm": bfl,
        "back_focal_length_mm": bfl,
        "image_distance_mm": image_distance,
        "f_number": _scalar(fno),
        "epd_mm": _scalar(epd),
        "entrance_pupil_position_mm": _scalar(p.EPL()),
        "entrance_pupil_diameter_mm": _scalar(epd),
        "exit_pupil_position_mm": _scalar(p.XPL()),
        "exit_pupil_diameter_mm": _scalar(p.XPD()),
        "total_track_mm": total_track,
        "lagrange_invariant": _scalar(invariant),
        "chromatic_shift_um": chromatic_shift_um,
        "telecentricity_deg": telecentricity_deg,
        "chief_ray_height_mm": chief_ray_height_mm,
    }
    raw["na_image"] = optics.na_from_fnum(raw["f_number"]) if math.isfinite(raw["f_number"]) and raw["f_number"] != 0 else math.nan
    raw["na_image_paraxial"] = raw["na_image"]
    raw["efl_spread_um"] = chromatic_shift_um
    raw["chief_ray_angle_paraxial_deg"] = telecentricity_deg
    if not optic.object_surface.is_infinite:
        raw["magnification"] = _scalar(p.magnification())

    results: dict[str, Any] = {}
    for key, value in raw.items():
        clean = _finite_or_none(value)
        if clean is None:
            warnings.append(f"{key} is not finite for this model (afocal or degenerate conjugate); reported as null")
        results[key] = clean
    results["primary_wavelength_um"] = primary_um
    results["per_wavelength_efl_mm"] = {k: (v if math.isfinite(v) else None) for k, v in per_wavelength_efl_mm.items()}
    if assessment:
        results["import_fidelity"] = assessment
    results["metric_definitions"] = {
        "back_focal_length_mm": "Last optical vertex to paraxial back focus for parallel input rays at primary wavelength; signed along the optical axis",
        "bfl_mm": "Compatibility alias for back_focal_length_mm (corrected from the former image-distance definition)",
        "image_distance_mm": "Last optical vertex to current image surface, independent of its focus",
        "na_image_paraxial": "1/(2*Optiland FNO); paraxial estimate, not a real-ray n*sin(u) measurement; verify working F/# and conjugates for finite or immersion systems",
        "na_image": "Compatibility alias for na_image_paraxial",
        "chief_ray_angle_paraxial_deg": "atan of paraxial image-space chief-ray slope at maximum field; signed, not a real-ray angle",
        "telecentricity_deg": "Compatibility alias for chief_ray_angle_paraxial_deg",
        "efl_spread_um": "max(EFL)-min(EFL) over declared wavelengths, not longitudinal best-focus shift",
        "chromatic_shift_um": "Compatibility alias for efl_spread_um",
    }

    units = {
        "efl_mm": "mm", "bfl_mm": "mm", "f_number": "1", "na_image": "1", "epd_mm": "mm",
        "entrance_pupil_position_mm": "mm", "entrance_pupil_diameter_mm": "mm",
        "exit_pupil_position_mm": "mm", "exit_pupil_diameter_mm": "mm", "total_track_mm": "mm",
        "lagrange_invariant": "mm", "chromatic_shift_um": "um", "telecentricity_deg": "deg",
        "chief_ray_height_mm": "mm", "magnification": "1", "primary_wavelength_um": "um",
        "per_wavelength_efl_mm": "mm",
        "back_focal_length_mm": "mm", "image_distance_mm": "mm", "na_image_paraxial": "1",
        "efl_spread_um": "um", "chief_ray_angle_paraxial_deg": "deg",
    }
    return {"results": results, "units": units, "warnings": warnings}


def evaluate_gate(results: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Check ``results`` (as returned by ``compute``) against a small pass/fail spec.

    ``spec`` maps a key from ``GATE_KEYS`` to a rule object combining any of
    ``min``, ``max``, or ``target`` with ``tol_pct`` (percent tolerance around
    target). All conditions declared for a key must hold for that key to pass;
    every key must pass for the gate overall to pass.
    """
    if not isinstance(spec, dict) or not spec:
        raise ValueError("gate specification must be a nonempty JSON object")
    checks = []
    overall = True
    for key, rule in spec.items():
        if key not in GATE_KEYS:
            raise ValueError(f"unknown gate key {key!r}; expected one of {sorted(GATE_KEYS)}")
        if not isinstance(rule, dict) or not rule:
            raise ValueError(f"gate rule for {key!r} must be a nonempty JSON object")
        unknown = set(rule) - {"min", "max", "target", "tol_pct"}
        if unknown:
            raise ValueError(f"unknown gate rule field(s) for {key!r}: {sorted(unknown)}")
        for field in ("min", "max", "target", "tol_pct"):
            if field in rule and (isinstance(rule[field], bool)
                                  or not isinstance(rule[field], (int, float))
                                  or not math.isfinite(rule[field])):
                raise ValueError(f"gate rule {key!r}.{field} must be a finite number, not a boolean")
        if "tol_pct" in rule and "target" not in rule:
            raise ValueError(f"gate rule {key!r}: tol_pct requires a target")
        if rule.get("tol_pct", 0) < 0:
            raise ValueError(f"gate rule {key!r}: tol_pct must be nonnegative")
        if "min" in rule and "max" in rule and rule["min"] > rule["max"]:
            raise ValueError(f"gate rule {key!r}: min must not exceed max")
        value = results.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            checks.append({"key": key, "value": None, "pass": False,
                           "reason": "not available as a finite numeric measurement for this model"})
            overall = False
            continue
        ok = True
        reasons = []
        if "min" in rule and value < rule["min"]:
            ok = False
            reasons.append(f"{value:.6g} < min {rule['min']:.6g}")
        if "max" in rule and value > rule["max"]:
            ok = False
            reasons.append(f"{value:.6g} > max {rule['max']:.6g}")
        if "target" in rule:
            target = rule["target"]
            tol_pct = rule.get("tol_pct", 0.0)
            # Finite inputs can still overflow float multiplication/subtraction.
            # Exact ratios preserve inclusive bounds without creating infinity.
            allowed = abs(Fraction(target)) * Fraction(tol_pct) / 100
            if abs(Fraction(value) - Fraction(target)) > allowed:
                ok = False
                reasons.append(f"{value:.6g} outside target {target:.6g} ± {tol_pct:g}%")
        checks.append({"key": key, "value": value, "pass": ok,
                       "reason": None if ok else "; ".join(reasons)})
        overall = overall and ok
    return {"pass": overall, "checks": checks}
