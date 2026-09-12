"""Strict numeric equivalence with coverage, declared units, and analysis identity.

Curves require identical coordinates and ordering; no interpolation is performed.
Absolute tolerances are expressed in each reference (A) metric's units.
"""
from __future__ import annotations

import math


def flatten(value, prefix: str = "") -> dict[str, float]:
    out: dict[str, float] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            out.update(flatten(child, f"{prefix}{key}."))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            out.update(flatten(child, f"{prefix}{index}."))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        out[prefix[:-1]] = float(value)
    return out


def validate_document(document, section: str) -> None:
    if not isinstance(document, dict):
        raise ValueError("JSON root must be an object")  # noqa: TRY004
    if section in document and not isinstance(document[section], (dict, list)):
        raise ValueError(f"{section} must be an object or array")
    if "units" in document and not isinstance(document["units"], dict):
        raise ValueError("units must be an object")

    def check(value):
        if isinstance(value, dict):
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("JSON numeric values must be finite")
    check(document)


def _identity_key(key: str) -> bool:
    key = key.lower()
    families = ("field", "wavelength", "configuration", "config", "pupil", "analysis",
                "frequency", "frequencies", "coordinate", "sampling", "normalization")
    return (key in {"metadata", "settings", "grid", "padding", "n_fft", "na", "fnum",
                    "f_number", "numerical_aperture", "npix", "pad", "scheme",
                    "removed_terms", "nan_semantics"}
            or any(key == family or key == family + "s" or key.startswith((family + "_", family + "s_"))
                   for family in families))


def _identities(value, prefix="") -> dict:
    out = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}{key}"
            if _identity_key(key):
                out[path] = child
            elif key != "units":
                out.update(_identities(child, path + "."))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.update(_identities(child, f"{prefix}{index}."))
    return out


def _labels(value, prefix="") -> dict:
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            out.update(_labels(child, f"{prefix}{key}."))
        return out
    if isinstance(value, list):
        out = {}
        for index, child in enumerate(value):
            out.update(_labels(child, f"{prefix}{index}."))
        return out
    return {} if isinstance(value, (int, float)) and not isinstance(value, bool) else {prefix[:-1]: value}


# Scale to mm, radians, or cycles/mm. Unlisted labels must match exactly.
_UNITS = {
    "m": ("length", 1000.0), "cm": ("length", 10.0), "mm": ("length", 1.0),
    "um": ("length", 0.001), "nm": ("length", 0.000001),
    "rad": ("angle", 1.0), "mrad": ("angle", 0.001),
    "deg": ("angle", math.pi / 180), "arcsec": ("angle", math.pi / 648000),
    "cyc/mm": ("frequency", 1.0), "cyc/um": ("frequency", 1000.0),
    "lp/mm": ("frequency", 1.0), "lp/um": ("frequency", 1000.0),
    "1": ("dimensionless", 1.0), "dimensionless": ("dimensionless", 1.0),
    "%": ("dimensionless", 0.01),
}


def _unit(units, metric, section):
    paths = [metric]
    if section and metric.startswith(section + "."):
        paths.append(metric[len(section) + 1:])
    # Most-specific declaration wins, with parent units inherited by array leaves.
    for path in paths:
        parts = path.split(".")
        while parts:
            key = ".".join(parts)
            if key in units:
                value = units[key]
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"invalid unit declaration for {key}")
                return value.strip().replace("µ", "u").replace("μ", "u")
            parts.pop()
    return None


def _factor(a, b):
    if a == b:
        return 1.0
    if a is None or b is None:
        raise ValueError("unit declared on only one side")
    if a not in _UNITS or b not in _UNITS or _UNITS[a][0] != _UNITS[b][0]:
        raise ValueError(f"incompatible or unsupported units: {a!r}, {b!r}")
    return _UNITS[b][1] / _UNITS[a][1]


def compare_documents(a: dict, b: dict, *, rtol=0.01, atol=0.0, section="results",
                      shared_only=False, required=()) -> dict:
    """Return an equivalence report; raises ValueError for invalid input/tolerances."""
    if any(not math.isfinite(t) or t < 0 for t in (rtol, atol)):
        raise ValueError("tolerances must be finite and nonnegative")
    for document in (a, b):
        validate_document(document, section)
    da = {section: a.get(section, {})} if section else a
    db = {section: b.get(section, {})} if section else b
    ia, ib = _identities(a), _identities(b)
    fa, fb = flatten(da), flatten(db)
    # Coordinates/settings establish identity, and do not count as measured coverage.
    for flat, identities in ((fa, ia), (fb, ib)):
        for key in list(flat):
            if any(key == ident or key.startswith(ident + ".") for ident in identities):
                del flat[key]
    shared = sorted(fa.keys() & fb.keys())
    only_a, only_b = sorted(fa.keys() - fb.keys()), sorted(fb.keys() - fa.keys())
    required = [f"{section}.{key}" if section and not key.startswith(section + ".") else key
                for key in required]
    missing = sorted(set(required) - set(shared))
    reasons = []
    if not shared:
        reasons.append("no shared numeric metrics")
    if missing:
        reasons.append("required numeric metrics are missing")
    if not shared_only:
        if only_a or only_b:
            reasons.append("numeric metric coverage differs")
        if ia != ib:
            reasons.append("analysis identity differs or is missing")
        if _labels(da) != _labels(db):
            reasons.append("result labels or nonnumeric values differ")
    diffs, exceeded, unit_errors = {}, [], {}
    for key in shared:
        x, y = fa[key], fb[key]
        unit = None
        if not shared_only:
            try:
                unit = _unit(a.get("units", {}), key, section)
                y *= _factor(unit, _unit(b.get("units", {}), key, section))
            except ValueError as error:
                unit_errors[key] = str(error)
                continue
        absd = abs(x - y)
        threshold = atol + rtol * abs(x)
        if not all(math.isfinite(v) for v in (y, absd, threshold)):
            unit_errors[key] = "numeric comparison overflow"
            continue
        relative = absd / abs(x) if x else (0.0 if absd == 0 else None)
        if relative is not None and not math.isfinite(relative):
            relative = None
        ok = absd <= threshold
        diffs[key] = {"a": x, "b": y, "abs": absd, "rel": relative, "ok": ok, "unit": unit}
        if not ok:
            exceeded.append(key)
    if unit_errors:
        reasons.append("units or numeric ranges are not comparable")
    passed = not reasons and not exceeded
    status = ("incomparable" if reasons else "exploratory" if shared_only
              else "equivalent" if passed else "different")
    return {"status": status, "equivalent": None if shared_only else passed,
            "all_within_tolerance": passed, "exceeded": exceeded, "diffs": diffs,
            "only_in_a": only_a, "only_in_b": only_b, "missing_required": missing,
            "incomparable_reasons": reasons, "unit_errors": unit_errors,
            "numeric_coverage": {"a": len(fa), "b": len(fb), "shared": len(shared),
                                 "compared": len(diffs)}}
