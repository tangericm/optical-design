"""Shared CLI contract for optical-design scripts.

Envelope schema version 1:
{schema, tool, subcommand, tier, inputs, results, units, method, warnings}
Exit codes: 0 ok, 2 usage, 3 missing tier dependency, 4 analysis failed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import math
import platform
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
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
    provenance: dict[str, Any] = field(default_factory=dict)

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


def _write(out: Any, text: str) -> None:
    """Write text to out; degrade gracefully on narrow console encodings (e.g. Windows cp1252)."""
    try:
        out.write(text)
    except UnicodeEncodeError:
        encoding = getattr(out, "encoding", None) or "ascii"
        safe = text.encode(encoding, errors="replace").decode(encoding)
        out.write(safe)


def emit(env: Envelope, as_json: bool, out=None) -> None:
    """Write the envelope. JSON is strict: NaN and Infinity are rejected, not emitted."""
    out = out or sys.stdout
    if as_json:
        out.write(json.dumps(env.to_dict(), indent=2, sort_keys=True, allow_nan=False,
                             default=_json_default) + "\n")
        return
    _write(out, f"{env.tool} {env.subcommand} (tier {env.tier})\n")
    _write(out, f"  method: {env.method}\n")
    for key, value in env.results.items():
        unit = env.units.get(key, "")
        _write(out, f"  {key:<30} {_fmt(value)} {unit}".rstrip() + "\n")
    for warning in env.warnings:
        _write(out, f"  warning: {warning}\n")


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


def finite_float(text: str) -> float:
    """argparse type that excludes NaN and both infinities."""
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid float value: {text!r}") from None
    if not math.isfinite(value):
        raise argparse.ArgumentTypeError(f"must be finite, got {text}")
    return value


def positive_float(text: str) -> float:
    """argparse type for a finite, strictly positive physical quantity."""
    value = finite_float(text)
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be greater than 0, got {text}")
    return value


def nonnegative_float(text: str) -> float:
    value = finite_float(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"must be nonnegative, got {text}")
    return value


def nonnegative_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid integer: {text!r}") from None
    if value < 0:
        raise argparse.ArgumentTypeError(f"must be nonnegative, got {text}")
    return value


def positive_int(text: str) -> int:
    value = nonnegative_int(text)
    if value == 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return value


def _input_hashes(args: argparse.Namespace) -> dict[str, Any]:
    """Hash recognized file inputs before execution, including coefficient files.

    Store argument identity and digest only; no host, user, environment or path data.
    """
    files = {}
    for key in ("map", "phase", "frames", "coeffs", "a", "b", "model", "spec"):
        value = getattr(args, key, None)
        if isinstance(value, str) and Path(value).is_file():
            path = Path(value)
            with path.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            files[key] = {"sha256": digest, "size_bytes": path.stat().st_size}
    return files


def _runtime_provenance(input_files: dict[str, Any]) -> dict[str, Any]:
    dependencies = {}
    for module, distribution in (("numpy", "numpy"), ("scipy", "scipy"),
                                 ("skimage", "scikit-image"), ("zospy", "zospy"),
                                 ("optiland", "optiland")):
        if module in sys.modules:
            try:
                dependencies[distribution] = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                dependencies[distribution] = "unavailable"
    return {"python_version": platform.python_version(), "dependencies": dependencies,
            "input_files": input_files}


def run(build_parser, argv: list[str] | None = None) -> int:
    """Parse argv, run the subcommand, emit the envelope; map failures to exit codes.

    ValueError (bad scheme, non-square map, wrong frame count) is a usage error (2);
    unreadable or unparseable input files are an analysis failure (4). A ValueError raised
    while emitting the result (json.dumps(allow_nan=False) rejecting a non-finite value) is
    also an analysis failure (4), not a usage error — the arguments were fine, the computed
    result wasn't — so that case is caught separately, inside the outer try but before it
    can reach the generic ValueError -> usage-error handler below.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        input_files = _input_hashes(args)
        env = args.func(args.sub, args)
        env.provenance = {**_runtime_provenance(input_files), **env.provenance}
        try:
            emit(env, as_json=args.json)
        except ValueError as e:
            fail(f"could not emit result: {e}", EXIT_ANALYSIS)
    except json.JSONDecodeError as e:                       # subclass of ValueError
        fail(f"could not parse JSON input: {e}", EXIT_ANALYSIS)
    except ValueError as e:
        parser.error(str(e))
    except OSError as e:
        fail(f"could not read input: {e}", EXIT_ANALYSIS)
    return EXIT_OK


def common_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parent


def parse_floats(text: str) -> list[float]:
    """Parse '0.1, 0.2,0.3' or a path to a JSON list / newline file into floats."""
    path = Path(text)
    if path.is_file():
        raw = path.read_text(encoding="utf-8").strip()
        if raw.startswith("["):
            raw_values = json.loads(raw)
            if not all(type(v) in (int, float) for v in raw_values):
                raise ValueError("coefficient JSON must contain only real numbers")
            values = [float(v) for v in raw_values]
        else:
            values = [float(v) for v in raw.replace(",", " ").split()]
    else:
        values = [float(v) for v in text.replace(",", " ").split()]
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("coefficients must be a nonempty list of finite numbers")
    return values
