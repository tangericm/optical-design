# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect a .zmx or Optiland-native .json prescription: surfaces, fields, wavelengths,
aperture, and (for .zmx) which Zemax directives shaped the model Optiland built versus
which were preserved, display metadata, unsupported with possible optical effect, or unknown.

Loads .zmx files with Optiland's own reader (optiland.fileio.load_zemax_file), not the
portable backend's directive allowlist. Parsing success is not a fidelity guarantee;
unknown and unsupported content remains visible, and non-mm files have raw length
labels. Read-only: the input file is hashed and read, never written.

    uv run --python 3.11 --with optiland==0.6.2 inspect_zmx.py --model lens.zmx --json

Exit codes: 0 ok, 2 usage, 3 optiland missing, 4 the file could not be parsed (message
from Optiland's own reader).
"""
from __future__ import annotations

import argparse
import hashlib
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100

TOOL = "inspect_zmx"

# Compatibility import for callers of the old inspection classifier.
from _lib.import_fidelity import classify, load_assessed_model

_classify = classify


def _json_safe(value: float) -> float | str:
    if math.isfinite(value):
        return value
    if math.isnan(value):
        return "NaN"
    return "Infinity" if value > 0 else "-Infinity"


def _material_name(material, wavelength_um: float) -> str:
    name = getattr(material, "name", None)
    if isinstance(name, str) and name:
        return name
    n = material.n(wavelength_um)
    n = float(n.item() if hasattr(n, "item") else n)
    if type(material).__name__ == "IdealMaterial" and abs(n - 1.0) < 1e-9:
        return "AIR"
    return f"n={n:.6g}"


def _surface_table(optic) -> tuple[list[dict], int]:
    surfaces = optic.surfaces
    radii = surfaces.radii
    conics = surfaces.conic
    wavelength_um = optic.primary_wavelength
    y_marginal, _ = optic.paraxial.marginal_ray()
    n_surfaces = surfaces.num_surfaces
    rows = []
    element_count = 0
    for index, surface in enumerate(surfaces.surfaces):
        if index == 0:
            kind = "object"
        elif index == n_surfaces - 1:
            kind = "image"
        else:
            kind = str(surface.surface_type or "standard")
        material = _material_name(surface.material_post, wavelength_um)
        if material not in ("AIR",) and index != n_surfaces - 1:
            element_count += 1
        rows.append({
            "index": index,
            "type": kind,
            "radius_mm": _json_safe(float(radii[index])),
            "thickness_mm": _json_safe(float(surface.thickness)),
            "material": material,
            "conic": float(conics[index]),
            "semi_diameter_mm": abs(float(y_marginal[index].item() if hasattr(y_marginal[index], "item")
                                          else y_marginal[index])),
            "is_stop": bool(surface.is_stop),
        })
    return rows, element_count


def _fields_block(optic) -> dict:
    field_definition = optic.fields.field_definition
    field_type = type(field_definition).__name__.removesuffix("Field") if field_definition else "unknown"
    values = [{"x": f.x, "y": f.y, "vx": f.vx, "vy": f.vy, "weight": f.weight} for f in optic.fields.fields]
    return {"type": field_type, "values": values, "telecentric": bool(optic.fields.telecentric)}


def _wavelengths_block(optic) -> dict:
    values = [float(w) for w in optic.wavelengths.get_wavelengths()]
    weights = [float(w) for w in optic.wavelengths.weights]
    return {"values_um": values, "weights": weights, "primary_um": float(optic.primary_wavelength),
           "primary_index": int(optic.wavelengths.primary_index)}


def inspect_model(model_path: str) -> tuple[dict, list[str]]:
    path = Path(model_path)
    raw = path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    warnings: list[str] = []
    suffix = path.suffix.lower()

    optic, assessment = load_assessed_model(path, allow_raw_units=True, raw=raw)
    warnings.extend(assessment["warnings"])
    if suffix == ".zmx":
        fmt = "Zemax sequential text"
    else:
        fmt = "Optiland JSON"

    aperture = optic.aperture
    surfaces, element_count = _surface_table(optic)
    if not assessment["numerical_analysis_allowed"]:
        surfaces = [{key.removesuffix("_mm") + "_raw" if key.endswith("_mm") else key: value
                     for key, value in row.items()} for row in surfaces]
    results = {
        "sha256": sha256,
        "format": fmt,
        "units": assessment["source_units"],
        "import_fidelity": assessment,
        "aperture_type": aperture.ap_type if aperture is not None else None,
        "aperture_value": float(aperture.value) if aperture is not None else None,
        "fields": _fields_block(optic),
        "wavelengths": _wavelengths_block(optic),
        "surfaces": surfaces,
        "element_count": element_count,
    }
    if "directives" in assessment:
        results["directives"] = assessment["directives"]
    return results, warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspect_zmx.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="example: uv run --with optiland==0.6.2 inspect_zmx.py --model lens.zmx --json")
    parser.add_argument("--model", required=True, help=".zmx or Optiland-native .json prescription")
    parser.add_argument("--json", action="store_true", help="emit the JSON envelope instead of a table")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    cli.require("optiland", "install with: uv run --with optiland==0.6.2 inspect_zmx.py ...")

    try:
        results, warnings = inspect_model(args.model)
    except ValueError as e:
        cli.fail(f"could not parse model: {e}", cli.EXIT_ANALYSIS)
    except OSError as e:
        cli.fail(f"could not read model: {e}", cli.EXIT_ANALYSIS)

    env = cli.Envelope(
        TOOL, "inspect", 1,
        inputs={"model": args.model},
        results=results, units={"aperture_value": results["units"] if results["aperture_type"] in {"EPD", "float_by_stop_size"} else "1"},
        warnings=warnings,
        method="Optiland 0.6.2 fileio.load_zemax_file / load_optiland_file; surface semi-diameters are "
               "the paraxial marginal ray height at each surface, not a declared mechanical aperture; "
               "shared import assessment distinguishes preserved content, display metadata, unsupported "
               "optical settings and unknown directives; parsing success does not establish fidelity.",
    )
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
