# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect a .zmx or Optiland-native .json prescription: surfaces, fields, wavelengths,
aperture, and (for .zmx) which Zemax directives shaped the model Optiland built versus
which were read as cosmetic metadata.

Loads .zmx files with Optiland's own reader (optiland.fileio.load_zemax_file), not the
portable backend's directive allowlist -- a real OpticStudio export carries dozens of
header lines (AUTH, ENVD, RAIM, GSTD, POLS, ...) that never reach the ray trace, and this
tool reports them as ignored rather than refusing the file outright. Read-only: the
input file is hashed and read, never written.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100

TOOL = "inspect_zmx"

# Directives that change the optical model Optiland traces (geometry, material,
# aperture, field, wavelength). Everything else is cosmetic or metadata that
# Optiland's Zemax reader either never looks at, or parses only into a display-only
# field (e.g. NAME). Kept close to Optiland 0.6.2's own operand table, but classified
# by optical effect rather than by "does the reader tokenize this line at all" -- e.g.
# NAME is tokenized but only sets a display string, so it is "ignored" here.
USED_DIRECTIVES = {
    "SURF", "TYPE", "CURV", "DISZ", "GLAS", "CONI", "PARM", "STOP", "DIAM",
    "ENPD", "FTYP", "XFLN", "YFLN", "WAVM", "PWAV", "UNIT", "MODE",
    "GCAT",  # resolves GLAS names to an index/Abbe pair; changes the traced glass
    "FNUM", "OBNA",  # alternate aperture specs, same optical role as ENPD
}
# Explicitly cosmetic/metadata directives, plus a few mechanical/display-only ones
# (SSID duplicates the SURF ordinal; MEMA/POPS/CLAP are mechanical or display
# apertures, not the optical clear aperture the trace uses).
IGNORED_DIRECTIVES = {
    "AUTH", "NAME", "NOTE", "VERS", "ENVD", "GFAC", "RAIM", "PUSH", "SDMA", "OMMA",
    "ROPD", "HYPR", "PICB", "FWGN", "POLS", "GLRS", "GSTD", "NSCD", "COFN", "LUID",
    "EERA", "FIMP", "HIDE", "MIRR", "SLAB", "FLAP", "PZUP", "MNUM", "MOFF",
    "SSID", "MEMA", "POPS", "IWDP", "PFIL", "LANG", "FLOA", "CLAP", "BLNK",
}
IGNORED_PREFIXES = ("VD", "VC", "VAN", "TOL")  # vignetting factors, tolerance blocks
KNOWN_SURFACE_TYPES = {"STANDARD", "EVENASPH", "PARAXIAL", "ODDASPHE"}


def _decode_zmx_text(raw: bytes) -> str:
    for encoding in ("utf-16", "utf-8-sig", "iso-8859-1"):
        try:
            return raw.decode(encoding)
        except UnicodeError:
            continue
    raise ValueError("could not decode as UTF-16, UTF-8 or Latin-1 text")  # pragma: no cover


def _classify(key: str) -> str:
    if key in USED_DIRECTIVES:
        return "used"
    if key in IGNORED_DIRECTIVES or key.startswith(IGNORED_PREFIXES):
        return "ignored"
    # Unrecognized token: Optiland's Zemax reader only acts on operands in its own
    # dispatch table and silently skips anything outside it, so an unlisted key did
    # not shape the model either.
    return "ignored"


def _scan_zmx_directives(text: str) -> dict:
    keys_seen: list[str] = []
    seen = set()
    surface_types: list[tuple[int, str]] = []
    current_surface = -1
    mnum_configs: int | None = None
    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        key = tokens[0]
        if key not in seen:
            seen.add(key)
            keys_seen.append(key)
        if key == "SURF":
            try:
                current_surface = int(tokens[1])
            except (IndexError, ValueError):
                current_surface += 1
        elif key == "TYPE" and current_surface >= 0 and len(tokens) > 1:
            surface_types.append((current_surface, tokens[1]))
        elif key == "MNUM" and mnum_configs is None and len(tokens) > 1:
            try:
                mnum_configs = int(tokens[1])
            except ValueError:
                pass
    return {"keys": keys_seen, "surface_types": surface_types, "mnum_configs": mnum_configs}


def _unit_directive(text: str) -> str | None:
    for line in text.splitlines():
        tokens = line.split()
        if tokens and tokens[0] == "UNIT" and len(tokens) > 1:
            return tokens[1]
    return None


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
    from optiland.fileio import load_optiland_file, load_zemax_file

    path = Path(model_path)
    raw = path.read_bytes()
    sha256 = hashlib.sha256(raw).hexdigest()
    warnings: list[str] = []
    suffix = path.suffix.lower()

    directives = None
    if suffix == ".zmx":
        fmt = "Zemax sequential text"
        text = _decode_zmx_text(raw)
        scan = _scan_zmx_directives(text)
        directives = [{"key": key, "used": _classify(key) == "used"} for key in scan["keys"]]

        declared_unit = _unit_directive(text)
        if declared_unit is not None and declared_unit.upper() != "MM":
            warnings.append(
                f"file declares UNIT {declared_unit}, but Optiland 0.6.2's Zemax reader does not convert "
                "non-millimetre units -- reported lengths are the raw file values, not millimetres")
        # MNUM's total-configurations count is what distinguishes a real multi-config file
        # from the single boilerplate MOFF/MNUM row every Zemax export carries. Likewise,
        # NSCD is a fixed-size default block present even in purely sequential files; only a
        # distinct NSC* token (an actual non-sequential object row) indicates real NSC content.
        if scan["mnum_configs"] is not None and scan["mnum_configs"] > 1:
            warnings.append(f"file declares {scan['mnum_configs']} configurations (MOFF/MNUM); only "
                            "the loaded default configuration is reflected here")
        if any(key.startswith("NSC") and key != "NSCD" for key in scan["keys"]):
            warnings.append("file contains non-sequential component data (NSC*); non-sequential "
                            "geometry is not represented in this sequential inspection")
        coordbrk_surfaces = [i for i, t in scan["surface_types"] if t == "COORDBRK"]
        if coordbrk_surfaces:
            warnings.append(f"surface(s) {coordbrk_surfaces} use TYPE COORDBRK (coordinate break); "
                            "the system may not be centered in the usual sequential sense")
        other_unusual = sorted({t for i, t in scan["surface_types"]
                                if t not in KNOWN_SURFACE_TYPES and t != "COORDBRK"})
        if other_unusual:
            warnings.append(f"surface TYPE(s) {other_unusual} are outside STANDARD/EVENASPH/PARAXIAL/"
                            "ODDASPHE; verify Optiland traced the intended geometry")
        optic = load_zemax_file(str(path))
    elif suffix == ".json":
        fmt = "Optiland JSON"
        optic = load_optiland_file(str(path))
    else:
        raise ValueError(f"unsupported model file extension {suffix!r}: expected .zmx or .json")

    aperture = optic.aperture
    surfaces, element_count = _surface_table(optic)
    results = {
        "sha256": sha256,
        "format": fmt,
        "units": "mm",
        "aperture_type": aperture.ap_type if aperture is not None else None,
        "aperture_value": float(aperture.value) if aperture is not None else None,
        "fields": _fields_block(optic),
        "wavelengths": _wavelengths_block(optic),
        "surfaces": surfaces,
        "element_count": element_count,
    }
    if directives is not None:
        results["directives"] = directives
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
        results=results, units={"aperture_value": "mm" if results["aperture_type"] == "EPD" else "1"},
        warnings=warnings,
        method="Optiland 0.6.2 fileio.load_zemax_file / load_optiland_file; surface semi-diameters are "
               "the paraxial marginal ray height at each surface, not a declared mechanical aperture; "
               "directive classification reflects optical effect on the traced model, not merely whether "
               "Optiland's reader tokenizes the line.",
    )
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
