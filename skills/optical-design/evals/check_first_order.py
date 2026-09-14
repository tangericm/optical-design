# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print ground-truth first-order values for a .zmx or Optiland .json model.

Graders use this as an independent check on what an agent reports: EFL, BFL, F/#,
EPD, total track, per-wavelength EFL (reveals axial color) and the real-ray
image-space chief-ray angle at the largest declared field (telecentricity error).

Optiland is imported lazily so `--help` and argument errors do not require it
installed. Install it with, e.g.:

    uv run --python 3.11 --with optiland==0.6.2 evals/check_first_order.py MODEL

Usage:
    check_first_order.py MODEL.zmx
    check_first_order.py MODEL.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_optic(path: Path):
    try:
        import optiland.fileio as fileio
    except ImportError:
        print(
            "optiland is required but not installed. Run with, e.g.:\n"
            "  uv run --python 3.11 --with optiland==0.6.2 "
            f"{Path(__file__).name} {path}",
            file=sys.stderr,
        )
        raise SystemExit(3)

    suffix = path.suffix.lower()
    if suffix == ".zmx":
        return fileio.load_zemax_file(str(path))
    if suffix == ".json":
        return fileio.load_optiland_file(str(path))
    print(f"unsupported model extension: {suffix!r} (expected .zmx or .json)", file=sys.stderr)
    raise SystemExit(2)


def _scalar(x) -> float:
    """Reduce a possibly-array-backed Optiland scalar to a plain Python float."""
    import numpy as np

    arr = np.asarray(x)
    return float(arr.reshape(-1)[0])


def _per_wavelength_efl(optic) -> dict:
    """Replicate Paraxial.f2() at every declared wavelength.

    Optiland's own f2()/FNO() always use optic.primary_wavelength; this repeats
    the same marginal-ray trace at each wavelength to expose axial color.
    """
    p = optic.paraxial
    z_start = p.surfaces.positions[1] - 1
    out = {}
    for w in optic.wavelengths.get_wavelengths():
        y, u = p.trace_generic(1.0, 0.0, z_start, w)
        out[f"{w:.4f}"] = _scalar(-y[0] / u[-1])
    return out


def _max_field_chief_ray_angle_deg(optic) -> float | None:
    """Real-ray image-space chief-ray angle (from the axis) at the largest field.

    Assumes the model's declared fields vary in normalized Hy only (true for
    every form in assets/forms/); returns None if there is no off-axis field.
    """
    import numpy as np

    coords = optic.fields.get_field_coords()
    if len(coords) < 2:
        return None
    hx, hy = max(coords, key=lambda c: abs(c[0]) + abs(c[1]))
    if abs(hx) < 1e-12 and abs(hy) < 1e-12:
        return None
    wl = optic.primary_wavelength
    optic.trace_generic(Hx=hx, Hy=hy, Px=0.0, Py=0.0, wavelength=wl)
    ell = np.asarray(optic.surfaces.L[-1, 0])
    m = np.asarray(optic.surfaces.M[-1, 0])
    n = np.asarray(optic.surfaces.N[-1, 0])
    transverse = float(np.hypot(ell, m).reshape(-1)[0])
    axial = float(np.asarray(n).reshape(-1)[0])
    return float(np.degrees(np.arctan2(transverse, axial)))


def first_order_summary(path: Path) -> dict:
    optic = _load_optic(path)
    p = optic.paraxial

    thicknesses = [_scalar(s.thickness) for s in optic.surfaces.surfaces]
    bfl = thicknesses[-2] if len(thicknesses) >= 2 else None

    result = {
        "path": str(path),
        "efl_mm": _scalar(p.f2()),
        "bfl_mm": bfl,
        "f_number": _scalar(p.FNO()),
        "epd_mm": _scalar(p.EPD()),
        "total_track_mm": _scalar(optic.total_track),
        "primary_wavelength_um": _scalar(optic.primary_wavelength),
        "efl_mm_per_wavelength_um": _per_wavelength_efl(optic),
        "image_space_chief_ray_angle_deg_at_max_field": _max_field_chief_ray_angle_deg(optic),
    }
    if abs(result["efl_mm"]) > 1.0e5:
        result["note"] = "afocal (paraxial EFL diverges); read bfl/f_number as not meaningful"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="path to a .zmx or Optiland .json model")
    args = parser.parse_args(argv)

    if not args.model.exists():
        print(f"no such file: {args.model}", file=sys.stderr)
        return 2

    summary = first_order_summary(args.model)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
