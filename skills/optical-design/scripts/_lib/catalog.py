"""Local, declared catalog metadata: strict bounds and deterministic target ranking."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
from pathlib import Path

UNITS = {"m": ("length", 1000.), "cm": ("length", 10.), "mm": ("length", 1.),
         "um": ("length", .001), "nm": ("length", .000001),
         "rad": ("angle", 1.), "deg": ("angle", math.pi/180), "1": ("dimensionless", 1.)}
IDENTITY = {"vendor", "part", "source", "retrieved_on", "model"}


def _object(value, allowed, required, label):
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - allowed:
        raise ValueError(f"{label}: required keys {sorted(required)}; allowed keys {sorted(allowed)}")


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{label} must be a nonempty string without outer whitespace")


def _number(value, label):
    try:
        valid = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{label} must be a finite number")


def _unit(value):
    if not isinstance(value, str) or value not in UNITS:
        raise ValueError(f"unit must be one of {', '.join(UNITS)}")


def _root(data, collection):
    _object(data, {"schema", collection}, {"schema", collection}, collection)
    if type(data["schema"]) is not int or data["schema"] != 1:
        raise ValueError("catalog/query schema must be integer 1")
    if not isinstance(data[collection], list) or not data[collection]:
        raise ValueError(f"{collection} must be a nonempty list")


def validate_index(data):
    _root(data, "entries")
    seen = set()
    for row in data["entries"]:
        _object(row, IDENTITY | {"properties"}, IDENTITY | {"properties"}, "entry")
        for key in IDENTITY:
            _text(row[key], key)
        try:
            date = dt.date.fromisoformat(row["retrieved_on"])
        except ValueError:
            raise ValueError("retrieved_on must be a valid YYYY-MM-DD date") from None
        if date.isoformat() != row["retrieved_on"]:
            raise ValueError("retrieved_on must be a YYYY-MM-DD date")
        identity = row["vendor"], row["part"]
        if identity in seen:
            raise ValueError(f"duplicate vendor/part: {identity}")
        seen.add(identity)
        if not isinstance(row["properties"], dict) or not row["properties"]:
            raise ValueError("properties must be a nonempty object")
        for key, prop in row["properties"].items():
            _text(key, "property name")
            _object(prop, {"value", "unit"}, {"value", "unit"}, key)
            _number(prop["value"], key)
            _unit(prop["unit"])
    return data


def validate_query(data):
    _root(data, "constraints")
    seen = set()
    for c in data["constraints"]:
        _object(c, {"property", "unit", "min", "max", "target", "scale", "weight"},
                {"property", "unit"}, "constraint")
        _text(c["property"], "constraint property")
        _unit(c["unit"])
        if c["property"] in seen:
            raise ValueError("combine bounds for each property into a single constraint")
        seen.add(c["property"])
        if not {"min", "max"} & c.keys():
            raise ValueError("each constraint requires min or max")
        for key in ("min", "max", "target", "scale", "weight"):
            if key in c:
                _number(c[key], key)
        if c.get("min", -math.inf) > c.get("max", math.inf):
            raise ValueError("constraint min cannot exceed max")
        if "target" in c:
            if "scale" not in c or c["scale"] <= 0 or c.get("weight", 1) <= 0:
                raise ValueError("target requires positive scale and positive weight")
            if not c.get("min", -math.inf) <= c["target"] <= c.get("max", math.inf):
                raise ValueError("target must satisfy its hard bounds")
        elif {"scale", "weight"} & c.keys():
            raise ValueError("scale/weight require a target")
    return data


def match(index, query, limit=10):
    validate_index(index)
    validate_query(query)
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")
    matches, rejected = [], []
    for row in index["entries"]:
        evaluated, reasons, terms, weights = {}, [], [], []
        for c in query["constraints"]:
            name = c["property"]
            prop = row["properties"].get(name)
            if prop is None:
                reasons.append(f"{name}: missing property")
                continue
            src, dst = UNITS[prop["unit"]], UNITS[c["unit"]]
            if src[0] != dst[0]:
                reasons.append(f"{name}: incompatible units {prop['unit']} and {c['unit']}")
                continue
            value = prop["value"] * (src[1] / dst[1])
            if not math.isfinite(value):
                raise ValueError(f"{name}: unit conversion overflow")
            evaluated[name] = {"value": value, "unit": c["unit"]}
            if not c.get("min", -math.inf) <= value <= c.get("max", math.inf):
                reasons.append(f"{name}: outside inclusive bounds")
            if "target" in c:
                weight = c.get("weight", 1)
                term = weight * abs(value-c["target"]) / c["scale"]
                if not math.isfinite(term):
                    raise ValueError(f"{name}: ranking overflow; increase scale")
                terms.append(term)
                weights.append(weight)
        identity = {k: row[k] for k in sorted(IDENTITY)}
        if reasons:
            rejected.append({**identity, "reasons": reasons})
        else:
            if not math.isfinite(sum(terms)) or not math.isfinite(sum(weights)):
                raise ValueError("ranking sum overflow; rescale weights")
            score = sum(terms) / sum(weights) if weights else 0.0
            if not math.isfinite(score):
                raise ValueError("ranking sum overflow; rescale weights")
            matches.append({**identity, "score": score, "evaluated": evaluated})
    matches.sort(key=lambda r: (r["score"], r["vendor"], r["part"]))
    rejected.sort(key=lambda r: (r["vendor"], r["part"]))
    return {"status": "matches" if matches else "no_matches", "total_matches": len(matches),
            "matches": matches[:limit], "rejected": rejected, "source_verification": "declared_only"}


def load_json(path):
    """Hash the exact bytes parsed; source identifiers are metadata and never fetched."""
    raw = Path(path).read_bytes()
    def no_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=no_duplicates), {
        "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
