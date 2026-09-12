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


def cmd_gaussian(parser, args):
    lam_um = args.wavelength_um
    results, units, inputs = {}, {}, {"wavelength_um": lam_um, "m2": args.m2}
    if args.w0_um is not None:
        w0 = args.w0_um
        zr_um = optics.rayleigh_range(w0, lam_um, args.m2)
        results.update({"w0_um": w0, "rayleigh_range_mm": zr_um * 1e-3,
                        "divergence_half_angle_mrad": optics.divergence_half_angle_rad(w0, lam_um, args.m2) * 1e3})
        units.update({"w0_um": "um", "rayleigh_range_mm": "mm", "divergence_half_angle_mrad": "mrad"})
        inputs["w0_um"] = w0
        if args.z_mm is not None:
            results["beam_radius_at_z_um"] = optics.beam_radius(args.z_mm * 1e3, w0, zr_um)
            units["beam_radius_at_z_um"] = "um"
            inputs["z_mm"] = args.z_mm
    if args.input_w_mm is not None and args.focal_mm is not None:
        w0_mm = optics.focused_waist(lam_um * 1e-3, args.focal_mm, args.input_w_mm, args.m2)
        results["focused_waist_um"] = w0_mm * 1e3
        results["focused_rayleigh_range_mm"] = optics.rayleigh_range(w0_mm, lam_um * 1e-3, args.m2)
        units.update({"focused_waist_um": "um", "focused_rayleigh_range_mm": "mm"})
        inputs.update({"input_w_mm": args.input_w_mm, "focal_mm": args.focal_mm})
    if not results:
        parser.error("give --w0-um, or --input-w-mm with --focal-mm")
    return cli.Envelope(TOOL, "gaussian", 0, inputs=inputs, results=results, units=units,
                        method="Gaussian beam: z_R = π w0²/(M² λ), θ = M² λ/(π w0), w(z) = w0 √(1+(z/z_R)²), focused w0 = M² λ f/(π w_in) (Saleh & Teich ch. 3)")


def cmd_oct_axial(parser, args):
    dz = optics.oct_axial_resolution(args.center_wavelength_um, args.bandwidth_nm * 1e-3, args.n)
    return cli.Envelope(TOOL, "oct-axial", 0,
                        inputs={"center_wavelength_um": args.center_wavelength_um, "bandwidth_nm": args.bandwidth_nm, "n": args.n},
                        results={"axial_resolution_um": dz, "coherence_length_um": 2 * dz * args.n},
                        units={"axial_resolution_um": "um", "coherence_length_um": "um"},
                        method="Δz = (2 ln2/π) λ0²/Δλ / n, Gaussian spectrum FWHM Δλ (Drexler & Fujimoto, OCT, ch. 2)")


def cmd_oct_lateral(parser, args):
    dx_mm = optics.oct_lateral_resolution(args.wavelength_um * 1e-3, args.focal_mm, args.beam_diameter_mm)
    return cli.Envelope(TOOL, "oct-lateral", 0,
                        inputs={"wavelength_um": args.wavelength_um, "focal_mm": args.focal_mm, "beam_diameter_mm": args.beam_diameter_mm},
                        results={"spot_diameter_um": dx_mm * 1e3, "confocal_parameter_mm": optics.confocal_parameter(dx_mm, args.wavelength_um * 1e-3),
                                 "effective_na": args.beam_diameter_mm / (2 * args.focal_mm)},
                        units={"spot_diameter_um": "um", "confocal_parameter_mm": "mm"},
                        method="Δx = 4 λ f/(π D) (1/e² diameters); b = π Δx²/(2 λ) (Drexler & Fujimoto ch. 2)")


def cmd_micro(parser, args):
    lam, na = args.wavelength_um, args.na
    results = {"rayleigh_um": optics.rayleigh(lam, na), "abbe_um": optics.abbe(lam, na),
               "fwhm_um": optics.airy_fwhm(lam, na), "axial_um": optics.micro_axial_resolution(lam, na, args.n)}
    units = {k: "um" for k in results}
    warnings = []
    if args.magnification is not None:
        nyq = optics.nyquist_pixel_at_camera(results["abbe_um"], args.magnification)
        results["nyquist_pixel_um"] = nyq
        units["nyquist_pixel_um"] = "um"
        if args.pixel_um is not None:
            results["sampling_ratio"] = nyq / args.pixel_um
            if args.pixel_um > nyq * 1.001:
                warnings.append(f"undersampled: pixel {args.pixel_um} µm exceeds Nyquist pixel {nyq:.3g} µm at {args.magnification}x")
    return cli.Envelope(TOOL, "micro", 0,
                        inputs={"wavelength_um": lam, "na": na, "n": args.n, "magnification": args.magnification, "pixel_um": args.pixel_um},
                        results=results, units=units, warnings=warnings,
                        method="Lateral: Rayleigh 0.61λ/NA, Abbe λ/(2NA), FWHM 0.51λ/NA; axial 2λn/NA²; Nyquist camera pixel = M·Abbe/2")


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
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--fnum", type=cli.positive_float)
        sub.add_argument("--na", type=cli.positive_float)

    add("airy", "Airy disk radius/diameter and FWHM", "airy --wavelength-um 0.55 --fnum 4", cmd_airy, aperture)
    add("rayleigh", "Rayleigh, Abbe and Sparrow two-point resolution", "rayleigh --wavelength-um 0.5 --na 0.5", cmd_rayleigh, aperture)

    def dof(sub):
        aperture(sub)
        sub.add_argument("--coc-um", type=float, help="allowed blur circle diameter for geometric DOF")
    add("dof", "Depth of focus (diffraction and geometric)", "dof --wavelength-um 0.55 --fnum 4", cmd_dof, dof)

    def telescope(sub):
        sub.add_argument("--diameter-mm", type=cli.positive_float, required=True)
        sub.add_argument("--wavelength-um", type=cli.positive_float, default=0.55)
    add("telescope", "Angular resolution: Rayleigh and Dawes", "telescope --diameter-mm 100", cmd_telescope, telescope)

    def gaussian(sub):
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--w0-um", type=cli.positive_float, help="waist radius (1/e²)")
        sub.add_argument("--z-mm", type=float, help="distance from waist for w(z)")
        sub.add_argument("--input-w-mm", type=cli.positive_float, help="collimated input 1/e² radius at the lens")
        sub.add_argument("--focal-mm", type=cli.positive_float)
        sub.add_argument("--m2", type=float, default=1.0)
    add("gaussian", "Gaussian beam waist, Rayleigh range, divergence, focused spot", "gaussian --wavelength-um 0.85 --input-w-mm 1 --focal-mm 50", cmd_gaussian, gaussian)

    def oct_axial(sub):
        sub.add_argument("--center-wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--bandwidth-nm", type=cli.positive_float, required=True, help="FWHM spectral bandwidth")
        sub.add_argument("--n", type=float, default=1.0, help="tissue refractive index")
    add("oct-axial", "OCT axial resolution from source bandwidth", "oct-axial --center-wavelength-um 0.84 --bandwidth-nm 50", cmd_oct_axial, oct_axial)

    def oct_lateral(sub):
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--focal-mm", type=cli.positive_float, required=True)
        sub.add_argument("--beam-diameter-mm", type=cli.positive_float, required=True, help="1/e² beam diameter at the objective")
    add("oct-lateral", "OCT lateral spot and confocal parameter", "oct-lateral --wavelength-um 0.84 --focal-mm 36 --beam-diameter-mm 3", cmd_oct_lateral, oct_lateral)

    def micro(sub):
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--na", type=cli.positive_float, required=True)
        sub.add_argument("--n", type=float, default=1.0, help="immersion index")
        sub.add_argument("--magnification", type=float)
        sub.add_argument("--pixel-um", type=cli.positive_float, help="camera pixel pitch")
    add("micro", "Microscope lateral/axial resolution and Nyquist pixel", "micro --wavelength-um 0.52 --na 0.8 --magnification 40 --pixel-um 6.5", cmd_micro, micro)

    return parser


def main(argv: list[str] | None = None) -> int:
    return cli.run(build_parser, argv)


if __name__ == "__main__":
    sys.exit(main())
