# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""PSF, MTF and sampling checks from a wavefront (Zernike coefficients or a map) (Tier 0)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli, fourier, optics  # noqa: E402, RUF100
from _lib import zernike as Z  # noqa: E402, RUF100
from zernike import coefficients_to_map, fit_map, load_map, rms_from_coeffs  # noqa: E402, RUF100

TOOL = "wavefront"


def _wavefront(parser, args, npix: int):
    if args.map:
        wmap_raw = load_map(args.map)
        if wmap_raw.shape[0] != wmap_raw.shape[1]:
            parser.error("map must be square")
        _, _, mask = Z.unit_disk(wmap_raw.shape[0])
        mask &= np.isfinite(wmap_raw)
        low_order_coeffs, _ = fit_map(wmap_raw, "fringe", 3, mask=mask)
        low_order, _ = coefficients_to_map("fringe", low_order_coeffs, npix=wmap_raw.shape[0])
        wmap = np.where(mask, wmap_raw - low_order, np.nan)
        rms = float(np.sqrt(np.nanmean(wmap[mask] ** 2)))
        return wmap, mask, rms, {"map": args.map}
    if args.coeffs is None or args.scheme is None:
        parser.error("give --scheme with --coeffs, or --map")
    coeffs = cli.parse_floats(args.coeffs)
    wmap, mask = coefficients_to_map(args.scheme, coeffs, npix=npix)
    return wmap, mask, rms_from_coeffs(args.scheme, coeffs), {"scheme": args.scheme, "coefficients": coeffs}


def _physical(results, units, args):
    if args.wavelength_um is not None and args.fnum is not None:
        lf = args.wavelength_um * args.fnum
        results["pixel_um"] = results["pixel_lambda_fnum"] * lf
        results["fwhm_um"] = results["fwhm_lambda_fnum"] * lf
        results["airy_radius_um"] = optics.airy_radius(args.wavelength_um, fnum=args.fnum)
        units.update({"pixel_um": "um", "fwhm_um": "um", "airy_radius_um": "um"})


def cmd_psf(parser, args):
    wmap, mask, rms, inputs = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad)
    results = {"strehl": res["strehl"], "rms_waves": rms, "fwhm_lambda_fnum": res["fwhm_lambda_fnum"],
               "encircled_energy_airy": res["encircled_energy_airy"], "pixel_lambda_fnum": res["pixel_lambda_fnum"]}
    units = {"rms_waves": "waves", "fwhm_lambda_fnum": "lambda*F#", "pixel_lambda_fnum": "lambda*F#"}
    _physical(results, units, args)
    warnings = []
    if rms <= 0.1:
        marechal = 1 - (2 * np.pi * rms) ** 2
        if abs(marechal - res["strehl"]) > 0.05:
            warnings.append(f"Strehl {res['strehl']:.3f} disagrees with Maréchal estimate {marechal:.3f}; check coefficient scheme/normalization")
    if args.out:
        np.save(args.out, res["psf"])
        results["psf_file"] = args.out
    method = "Fraunhofer PSF = |FFT(P·exp(2πiW))|², Strehl = peak / unaberrated peak, zero-padded ×pad (Goodman, Fourier Optics ch. 6)"
    if args.map:
        method += "; piston and tilt removed from map input"
    return cli.Envelope(TOOL, "psf", 0, inputs={**inputs, "npix": args.npix, "pad": args.pad, "wavelength_um": args.wavelength_um, "fnum": args.fnum},
                        results=results, units=units, warnings=warnings, method=method)


def cmd_mtf(parser, args):
    wmap, mask, rms, inputs = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad)
    nu, mx, my = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    results = {"strehl": res["strehl"], "rms_waves": rms}
    units = {"rms_waves": "waves"}
    warnings = []
    if args.wavelength_um is not None and args.fnum is not None:
        cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
        results["cutoff_cyc_per_mm"] = cutoff
        units["cutoff_cyc_per_mm"] = "cyc/mm"
        freqs = cli.parse_floats(args.freqs) if args.freqs else []
        if args.pixel_um is not None:
            nyq = 1000.0 / (2 * args.pixel_um)
            results["nyquist_cyc_per_mm"] = nyq
            units["nyquist_cyc_per_mm"] = "cyc/mm"
            freqs.append(nyq)
        results["mtf_at"] = {}
        for f in freqs:
            x = f / cutoff
            results["mtf_at"][f"{f:g}"] = {"x": float(np.interp(x, nu, mx)), "y": float(np.interp(x, nu, my)),
                                           "diffraction_limit": optics.mtf_diffraction(x)}
        if any(v["x"] > v["diffraction_limit"] + 0.02 for v in results["mtf_at"].values()):
            warnings.append("MTF exceeds the diffraction limit: numerical artifact, increase --pad/--npix")
    results["curve_nu_over_cutoff"] = nu[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_x"] = mx[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_y"] = my[::max(1, len(nu) // 50)].tolist()
    method = "MTF = |FFT(PSF)| normalized; diffraction limit (2/π)(acos x − x√(1−x²)), x = ν λ F# (Smith ch. 11)"
    if args.map:
        method += "; piston and tilt removed from map input"
    return cli.Envelope(TOOL, "mtf", 0, inputs={**inputs, "wavelength_um": args.wavelength_um, "fnum": args.fnum, "pixel_um": args.pixel_um, "freqs": args.freqs},
                        results=results, units=units, warnings=warnings, method=method)


def cmd_sample_check(parser, args):
    q = optics.sampling_q(args.wavelength_um, args.fnum, args.pixel_um)
    cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
    nyq = 1000.0 / (2 * args.pixel_um)
    warnings = []
    if q < 2:
        warnings.append(f"Q = {q:.2f} < 2: detector Nyquist ({nyq:.1f} cyc/mm) is below the optical cutoff ({cutoff:.1f} cyc/mm); the image aliases")
    return cli.Envelope(TOOL, "sample-check", 0,
                        inputs={"wavelength_um": args.wavelength_um, "fnum": args.fnum, "pixel_um": args.pixel_um},
                        results={"q": q, "cutoff_cyc_per_mm": cutoff, "nyquist_cyc_per_mm": nyq,
                                 "airy_radius_pixels": optics.airy_radius(args.wavelength_um, fnum=args.fnum) / args.pixel_um},
                        units={"cutoff_cyc_per_mm": "cyc/mm", "nyquist_cyc_per_mm": "cyc/mm", "airy_radius_pixels": "px"},
                        method="Q = λF#/p; Q = 2 is critically sampled (Fiete 1999, Opt. Eng. 38)", warnings=warnings)


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="wavefront.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run wavefront.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def source(sub):
        sub.add_argument("--scheme", choices=Z.SCHEMES)
        sub.add_argument("--coeffs", help="Zernike coefficients in waves")
        sub.add_argument("--map", help=".npy/.csv wavefront map in waves, NaN outside pupil")
        sub.add_argument("--wavelength-um", type=float)
        sub.add_argument("--fnum", type=float)
        sub.add_argument("--npix", type=int, default=128, help="pupil samples across (coefficient input)")
        sub.add_argument("--pad", type=int, default=8, help="FFT zero-padding factor")

    def psf(sub):
        source(sub)
        sub.add_argument("--out", help="save the normalized PSF grid as .npy")
    add("psf", "PSF, Strehl, FWHM and encircled energy from a wavefront", "psf --scheme fringe --coeffs 0,0,0,0.125 --wavelength-um 0.55 --fnum 4", cmd_psf, psf)

    def mtf(sub):
        source(sub)
        sub.add_argument("--pixel-um", type=float, help="detector pitch, adds MTF at Nyquist")
        sub.add_argument("--freqs", help="comma list of cyc/mm to report")
    add("mtf", "MTF curve with diffraction-limit comparison", "mtf --scheme noll --coeffs 0 --wavelength-um 0.5 --fnum 4 --pixel-um 5 --freqs 50,100", cmd_mtf, mtf)

    def sample(sub):
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--fnum", type=float, required=True)
        sub.add_argument("--pixel-um", type=float, required=True)
    add("sample-check", "Detector sampling Q vs. optical cutoff", "sample-check --wavelength-um 0.5 --fnum 4 --pixel-um 1", cmd_sample_check, sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
