"""Typed, finite requirements for the supported sequential-design workflow."""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from typing import Any

UNITS = {"efl_mm": "mm", "f_number": "1", "total_track_mm": "mm",
         "image_distance_mm": "mm", "rms_spot_um": "um", "mtf": "1"}
SCOPED = {"mtf", "rms_spot_um"}


def finite(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def metric_key(row: dict) -> str:
    name = row["metric"]
    if name in SCOPED:
        name += f"|f={row['field']}|w={row['wavelength']}"
    if row["metric"] == "mtf":
        name += f"|nu={float(row['frequency']):.17g}|axis={row['axis']}"
    return name


def _indices(values, name):
    if (not isinstance(values, list) or not values or
            any(type(v) is not int or v < 1 for v in values) or len(set(values)) != len(values)):
        raise ValueError(f"{name} must be unique positive, 1-based engine indices")
    return values


@dataclass(frozen=True)
class DesignSpec:
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, raw: dict) -> DesignSpec:
        if not isinstance(raw, dict) or raw.get("schema") != "1":
            raise ValueError("design specification requires schema '1'")
        data = copy.deepcopy(raw)
        allowed = {"schema", "name", "fields", "wavelengths", "frequencies_cyc_per_mm",
                   "requirements", "objective", "focus", "budget", "analysis", "minimum_gain"}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"unknown specification keys: {sorted(unknown)}")
        fields = _indices(data.get("fields"), "fields")
        wavelengths = _indices(data.get("wavelengths"), "wavelengths")
        freqs = data.setdefault("frequencies_cyc_per_mm", [])
        if not isinstance(freqs, list) or any(finite(v, "frequency") <= 0 for v in freqs):
            raise ValueError("frequencies must be positive numbers in cycles/mm")
        if len(set(freqs)) != len(freqs):
            raise ValueError("frequencies must be unique")
        requirements = data.get("requirements")
        if not isinstance(requirements, list) or not requirements:
            raise ValueError("at least one explicit requirement is needed")

        def validate_metric(row, extra):
            if not isinstance(row, dict) or row.get("metric") not in UNITS:
                raise ValueError(f"supported metrics are {sorted(UNITS)}")
            name = row["metric"]
            allowed = {'metric'} | extra
            if name in SCOPED:
                allowed |= {'field', 'wavelength'}
                if (type(row.get('field')) is not int or type(row.get('wavelength')) is not int or
                        row.get("field") not in fields or row.get("wavelength") not in wavelengths):
                    raise ValueError("metric field/wavelength must be included in analysis indices")
            if name == "mtf":
                allowed |= {'frequency', 'axis'}
                if finite(row.get('frequency'), 'metric frequency') not in freqs or row.get("axis") not in {"tangential", "sagittal"}:
                    raise ValueError("MTF metric requires an analyzed frequency and tangential/sagittal axis")
            if set(row) - allowed:
                raise ValueError(f'unknown metric keys: {sorted(set(row) - allowed)}')
            metric_key(row)

        ids = set()
        for req in requirements:
            validate_metric(req, {'id', 'unit', 'min', 'max'})
            if not isinstance(req.get("id"), str) or not req["id"] or req["id"] in ids:
                raise ValueError("each requirement needs a unique nonempty id")
            ids.add(req["id"])
            if req.get("unit") != UNITS[req["metric"]]:
                raise ValueError(f"{req['metric']} requires unit {UNITS[req['metric']]}")
            if "min" not in req and "max" not in req:
                raise ValueError("each requirement needs min and/or max")
            for bound in ("min", "max"):
                if bound in req:
                    finite(req[bound], bound)
            if req.get("min", -math.inf) > req.get("max", math.inf):
                raise ValueError("requirement min exceeds max")
        if "objective" in data:
            objective = data['objective']
            if isinstance(objective, dict) and ('terms' in objective or 'aggregation' in objective):
                if (set(objective) != {'direction', 'aggregation', 'terms'} or
                        objective.get('direction') != 'minimize' or
                        objective.get('aggregation') != 'weighted_rms'):
                    raise ValueError('composite objective requires direction minimize, aggregation weighted_rms and terms')
                terms = objective['terms']
                if not isinstance(terms, list) or not terms:
                    raise ValueError('composite objective requires a nonempty terms list')
                for term in terms:
                    validate_metric(term, {'unit', 'target', 'scale', 'weight'})
                    if term.get('unit') != UNITS[term['metric']]:
                        raise ValueError(f"{term['metric']} requires unit {UNITS[term['metric']]}")
                    finite(term.get('target'), 'objective target')
                    if finite(term.get('scale'), 'objective scale') <= 0:
                        raise ValueError('objective scale must be positive in metric units')
                    if finite(term.get('weight'), 'objective weight') <= 0:
                        raise ValueError('objective weight must be positive')
            else:
                validate_metric(objective, {'direction'})
                if objective.get("direction") not in {"minimize", "maximize"}:
                    raise ValueError("objective direction must be minimize or maximize")
        if "focus" in data:
            focus = data["focus"]
            if not isinstance(focus, dict) or set(focus) != {"min_mm", "max_mm"}:
                raise ValueError("focus requires min_mm and max_mm")
            lo, hi = finite(focus["min_mm"], "focus min"), finite(focus["max_mm"], "focus max")
            if lo <= 0 or lo >= hi:
                raise ValueError("focus requires 0 < min_mm < max_mm")
        budget = data.setdefault("budget", {})
        if not isinstance(budget, dict) or set(budget) - {"max_evaluations", "timeout_s"}:
            raise ValueError("budget supports max_evaluations and timeout_s")
        budget.setdefault("max_evaluations", 21)
        budget.setdefault("timeout_s", 120)
        if type(budget["max_evaluations"]) is not int or not 7 <= budget["max_evaluations"] <= 201:
            raise ValueError("max_evaluations must be an integer from 7 through 201")
        if finite(budget["timeout_s"], "timeout_s") <= 0:
            raise ValueError("timeout_s must be positive")
        analysis = data.setdefault("analysis", {})
        if not isinstance(analysis, dict) or set(analysis) - {"sampling", "use_polarization"}:
            raise ValueError("analysis supports sampling and use_polarization")
        analysis.setdefault("sampling", 64)
        analysis.setdefault("use_polarization", False)
        if analysis["sampling"] not in {32, 64, 128, 256} or type(analysis["sampling"]) is not int:
            raise ValueError("sampling must be 32, 64, 128 or 256")
        if type(analysis["use_polarization"]) is not bool:
            raise ValueError("use_polarization must be boolean")
        data.setdefault("minimum_gain", 0.001)
        if finite(data["minimum_gain"], "minimum_gain") < 0:
            raise ValueError("minimum_gain must be nonnegative in objective units")
        return cls(data)

    @property
    def objective(self):
        return self.data.get("objective")

    @property
    def objective_metrics(self) -> list[dict]:
        """Metric requests for both scalar and composite objectives, in term order."""
        if self.objective is None:
            return []
        return self.objective.get('terms', [self.objective])


def assess(spec: DesignSpec, measurements: list[dict]) -> dict:
    rows = {}
    for row in measurements:
        key = metric_key(row)
        if key in rows:
            raise ValueError(f"duplicate measurement: {key}")
        rows[key] = row
    results = []
    for req in spec.data["requirements"]:
        value = rows.get(metric_key(req))
        result = {"id": req["id"], "key": metric_key(req), "requirement": req}
        if value is None or value.get("value") is None:
            result.update(status="unavailable", reason=(value or {}).get("reason", "metric not returned"))
        elif value.get("unit") != req["unit"]:
            result.update(status="incomparable", reason="metric units differ")
        else:
            v = finite(value["value"], "measurement")
            passed = req.get("min", -math.inf) <= v <= req.get("max", math.inf)
            result.update(status="pass" if passed else "fail", value=v, unit=req["unit"])
        results.append(result)
    return {"passes": bool(results) and all(r["status"] == "pass" for r in results), "requirements": results}


def objective_breakdown(spec: DesignSpec, measurements: list[dict]) -> dict:
    """Evaluate merit and retain measured term evidence; never soften hard requirements."""
    if spec.objective is None:
        raise ValueError("refocus needs an explicit objective")
    rows = {}
    for row in measurements:
        key = metric_key(row)
        if key in rows:
            raise ValueError(f'duplicate measurement: {key}')
        rows[key] = row
    terms = []
    composite = spec.objective.get('aggregation') == 'weighted_rms'
    for request in spec.objective_metrics:
        key = metric_key(request)
        row = rows.get(key)
        unit = UNITS[request['metric']]
        if row is None or row.get('unit') != unit:
            raise ValueError(f'objective unavailable or incomparable: {key}')
        value = finite(row.get('value'), 'objective value')
        term = {k: request[k] for k in ('metric', 'field', 'wavelength', 'frequency', 'axis') if k in request}
        term.update(key=key, unit=unit, value=value)
        if composite:
            term.update(target=request['target'], scale=request['scale'], weight=request['weight'])
            residual = finite(value - request['target'], 'objective residual')
            term['normalized_residual'] = finite(residual / request['scale'], 'normalized objective residual')
        terms.append(term)
    if composite:
        # Taking square roots before ratios preserves even subnormal positive weights.
        # hypot avoids overflow from squaring otherwise representable residuals.
        root_max = math.sqrt(max(t['weight'] for t in terms))
        factors = [math.sqrt(t['weight']) / root_max for t in terms]
        denominator = math.hypot(*factors)
        for term, factor in zip(terms, factors):
            term['weighted_residual'] = factor / denominator * term['normalized_residual']
        value = finite(math.hypot(*(t['weighted_residual'] for t in terms)), 'objective value')
    else:
        value = terms[0]['value']
    return {'aggregation': 'weighted_rms' if composite else 'scalar',
            'direction': spec.objective['direction'], 'value': value,
            'unit': '1' if composite else terms[0]['unit'], 'terms': terms}


def objective_value(spec: DesignSpec, measurements: list[dict]) -> float:
    return objective_breakdown(spec, measurements)['value']
