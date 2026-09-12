# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolution, depth of focus, Gaussian beam, OCT, microscopy and telescope calculators (Tier 0)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli, optics  # noqa: E402, RUF100

TOOL = "resolve"


def _need_fnum_or_na(parser: argparse.ArgumentParser, args: argparse.Namespace) -> tuple[float, float]:
    if args.fnum is None and args.na is None:
        parser.error("one of --fnum or --na is required")
    fnum = args.fnum if args.fnum is not None else optics.fnum_from_na(args.na)
    na = args.na if args.na is not None else optics.na_from_fnum(args.fnum)
    return fnum, na


def cmd_airy(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    return cli.Envelope(
        TOOL, "airy", 0,
        inputs={"wavelength_um": lam, "fnum": fnum, "na": na},
        results={
            "airy_radius_um": optics.airy_radius(lam, fnum=fnum),
            "airy_diameter_um": 2 * optics.airy_radius(lam, fnum=fnum),
            "fwhm_um": optics.airy_fwhm(lam, na),
            "fnum": fnum, "na": na,
        },
        units={"airy_radius_um": "um", "airy_diameter_um": "um", "fwhm_um": "um"},
        method="Airy first zero 1.22 λ F# (Smith, Modern Optical Engineering); FWHM 0.51 λ/NA; paraxial NA = 1/(2F#)",
    )


def cmd_rayleigh(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    return cli.Envelope(
        TOOL, "rayleigh", 0,
        inputs={"wavelength_um": lam, "na": na, "fnum": fnum},
        results={
            "rayleigh_um": optics.rayleigh(lam, na),
            "abbe_um": optics.abbe(lam, na),
            "sparrow_um": optics.sparrow(lam, na),
            "fwhm_um": optics.airy_fwhm(lam, na),
        },
        units={k: "um" for k in ("rayleigh_um", "abbe_um", "sparrow_um", "fwhm_um")},
        method="Rayleigh 0.61λ/NA, Abbe λ/(2NA), Sparrow 0.47λ/NA (Hecht, Optics)",
    )


def cmd_dof(parser, args):
    fnum, na = _need_fnum_or_na(parser, args)
    lam = args.wavelength_um
    half = optics.dof_half_range(lam, na)
    results = {"diffraction_half_range_um": half, "diffraction_full_range_um": 2 * half, "fnum": fnum, "na": na}
    units = {"diffraction_half_range_um": "um", "diffraction_full_range_um": "um"}
    warnings = []
    if args.coc_um is not None:
        results["geometric_half_range_um"] = optics.dof_geometric_half(args.coc_um, fnum)
        units["geometric_half_range_um"] = "um"
        if results["geometric_half_range_um"] < half:
            warnings.append("blur-circle DOF is smaller than diffraction DOF: geometric limit governs")
    return cli.Envelope(
        TOOL, "dof", 0,
        inputs={"wavelength_um": lam, "fnum": fnum, "na": na, "coc_um": args.coc_um},
        results=results, units=units,
        method="Rayleigh quarter-wave DOF ±λ/(2NA²) = ±2λF#² (half range); full range 4λF#² (Smith ch. 4); geometric ±c·F#",
        warnings=warnings,
    )


def cmd_telescope(parser, args):
    d_mm, lam = args.diameter_mm, args.wavelength_um
    rad = optics.rayleigh_angular_rad(lam * 1e-3, d_mm)
    return cli.Envelope(
        TOOL, "telescope", 0,
        inputs={"diameter_mm": d_mm, "wavelength_um": lam},
        results={"rayleigh_arcsec": optics.rad_to_arcsec(rad), "rayleigh_rad": rad, "dawes_arcsec": optics.dawes_arcsec(d_mm)},
        units={"rayleigh_arcsec": "arcsec", "rayleigh_rad": "rad", "dawes_arcsec": "arcsec"},
        method="Rayleigh 1.22 λ/D; Dawes empirical 116/D[mm] arcsec",
    )


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="resolve.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_,
                              epilog=f"example: uv run resolve.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def aperture(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--fnum", type=float)
        sub.add_argument("--na", type=float)

    add("airy", "Airy disk radius/diameter and FWHM", "airy --wavelength-um 0.55 --fnum 4", cmd_airy, aperture)
    add("rayleigh", "Rayleigh, Abbe and Sparrow two-point resolution", "rayleigh --wavelength-um 0.5 --na 0.5", cmd_rayleigh, aperture)

    def dof(sub):
        aperture(sub)
        sub.add_argument("--coc-um", type=float, help="allowed blur circle diameter for geometric DOF")
    add("dof", "Depth of focus (diffraction and geometric)", "dof --wavelength-um 0.55 --fnum 4", cmd_dof, dof)

    def telescope(sub):
        sub.add_argument("--diameter-mm", type=float, required=True)
        sub.add_argument("--wavelength-um", type=float, default=0.55)
    add("telescope", "Angular resolution: Rayleigh and Dawes", "telescope --diameter-mm 100", cmd_telescope, telescope)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
