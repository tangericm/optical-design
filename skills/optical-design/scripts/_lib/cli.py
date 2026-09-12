"""Shared CLI contract for optical-design scripts.

Envelope schema version 1:
{schema, tool, subcommand, tier, inputs, results, units, method, warnings}
Exit codes: 0 ok, 2 usage, 3 missing tier dependency, 4 analysis failed.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, NoReturn

SCHEMA_VERSION = "1"
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_MISSING_DEP = 3
EXIT_ANALYSIS = 4


@dataclass
class Envelope:
    tool: str
    subcommand: str
    tier: int
    inputs: dict[str, Any]
    results: dict[str, Any]
    units: dict[str, str]
    method: str
    warnings: list[str] = field(default_factory=list)
    schema: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {_fmt(v)}" for k, v in value.items()) + "}"
    return str(value)


def emit(env: Envelope, as_json: bool, out=None) -> None:
    out = out or sys.stdout
    if as_json:
        out.write(json.dumps(env.to_dict(), indent=2, sort_keys=True, default=_json_default) + "\n")
        return
    out.write(f"{env.tool} {env.subcommand} (tier {env.tier})\n")
    out.write(f"  method: {env.method}\n")
    for key, value in env.results.items():
        unit = env.units.get(key, "")
        out.write(f"  {key:<30} {_fmt(value)} {unit}".rstrip() + "\n")
    for warning in env.warnings:
        out.write(f"  warning: {warning}\n")


def _json_default(value: Any) -> Any:
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        raise TypeError(f"not serializable: {type(value)!r}")
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not serializable: {type(value)!r}")


def require(module: str, hint: str):
    try:
        return importlib.import_module(module)
    except ImportError:
        sys.stderr.write(f"error: missing dependency '{module}'. {hint}\n")
        sys.exit(EXIT_MISSING_DEP)


def fail(message: str, code: int = EXIT_ANALYSIS) -> NoReturn:
    sys.stderr.write(f"error: {message}\n")
    sys.exit(code)


def common_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parent


def parse_floats(text: str) -> list[float]:
    """Parse '0.1, 0.2,0.3' or a path to a JSON list / newline file into floats."""
    from pathlib import Path

    path = Path(text)
    if path.is_file():
        raw = path.read_text(encoding="utf-8").strip()
        if raw.startswith("["):
            return [float(v) for v in json.loads(raw)]
        return [float(v) for v in raw.replace(",", " ").split()]
    return [float(v) for v in text.replace(",", " ").split()]
