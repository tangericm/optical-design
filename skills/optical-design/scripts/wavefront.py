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
import _lib.zernike as Z  # noqa: E402, RUF100
from _lib import cli, fourier, optics  # noqa: E402, RUF100
from _lib.wfmap import (  # noqa: E402, RUF100
    coefficients_to_map,
    fit_map,
    load_map,
    pupil_grid,
    rms_from_coeffs,
)

TOOL = "wavefront"


def _wavefront(parser, args, npix: int | None):
    """wavefront map, pupil mask, RMS in waves, envelope inputs and the pupil circle."""
    if args.pad < 2:
        parser.error("--pad must be >= 2 to avoid circular pupil autocorrelation")
    if (args.wavelength_um is None) != (args.fnum is None):
        parser.error("give both --wavelength-um and --fnum for physical units")
    if (args.pupil_center_px is None) != (args.pupil_radius_px is None):
        parser.error("give both --pupil-center-px and --pupil-radius-px")
    if args.map:
        if args.coeffs is not None or args.scheme is not None:
            parser.error("--map cannot be combined with --scheme/--coeffs")
        if npix is not None:
            parser.error("--npix is for coefficients; map samples are used without resampling")
        wmap_raw = load_map(args.map)
        if wmap_raw.ndim != 2 or wmap_raw.shape[0] != wmap_raw.shape[1]:
            parser.error("map must be square")
        pupil = None
        if args.pupil_center_px is not None:
            center = cli.parse_floats(args.pupil_center_px)
            if len(center) != 2:
                parser.error("--pupil-center-px requires row,col")
            pupil = {"center_px": center, "radius_px": args.pupil_radius_px}
        low_order_coeffs, _resid, pupil = fit_map(wmap_raw, "fringe", 3, pupil=pupil)
        mask = np.isfinite(wmap_raw) & pupil_grid(wmap_raw.shape, pupil)[2]
        low_order, _ = coefficients_to_map("fringe", low_order_coeffs, npix=wmap_raw.shape[0], pupil=pupil)
        wmap = np.where(mask, wmap_raw - low_order, np.nan)
        rms = float(np.sqrt(np.nanmean(wmap[mask] ** 2)))
        inputs = {"map": args.map, "npix": wmap_raw.shape[0], "nan_semantics": "opaque_aperture",
                  "pupil_geometry_source": "explicit" if args.pupil_center_px is not None else "inferred_circular_rim",
                  "pupil": {k: pupil[k] for k in ("center_px", "radius_px")},
                  "removed_terms": ["piston", "tilt_x", "tilt_y"]}
        return wmap, mask, rms, inputs, pupil
    if args.coeffs is None or args.scheme is None:
        parser.error("give --scheme with --coeffs, or --map")
    if args.pupil_center_px is not None:
        parser.error("explicit pupil geometry applies only to --map")
    npix = 128 if npix is None else npix
    if npix < 2:
        parser.error("--npix must be >= 2")
    coeffs = cli.parse_floats(args.coeffs)
    wmap, mask = coefficients_to_map(args.scheme, coeffs, npix=npix)
    pupil = {"center_px": [(npix - 1) / 2, (npix - 1) / 2], "radius_px": npix / 2}
    return wmap, mask, rms_from_coeffs(args.scheme, coeffs), {
        "scheme": args.scheme, "coefficients": coeffs, "npix": npix,
        "pupil": pupil, "pupil_geometry_source": "inscribed_unit_disk", "removed_terms": []}, pupil


def _model_warnings(args):
    warnings = []
    if args.map:
        warnings.append("NaN map pixels are opaque aperture, not missing measurements; no missing-data repair is performed")
        if args.pupil_center_px is None:
            warnings.append("Pupil circle inferred assuming a complete symmetric outer rim; supply explicit geometry for clipped or asymmetric pupils")
    return warnings


def _pupil_results(results, units, pupil):
    results["normalization_radius_px"] = pupil["radius_px"]
    results["pupil_center_px"] = pupil["center_px"]
    units.update({"normalization_radius_px": "px", "pupil_center_px": "px (row, col)"})


def _physical(results, units, args):
    if args.wavelength_um is not None and args.fnum is not None:
        lf = args.wavelength_um * args.fnum
        results["pixel_um"] = results["pixel_lambda_fnum"] * lf
        results["fwhm_um"] = results["fwhm_lambda_fnum"] * lf
        results["airy_radius_um"] = optics.airy_radius(args.wavelength_um, fnum=args.fnum)
        units.update({"pixel_um": "um", "fwhm_um": "um", "airy_radius_um": "um"})


def cmd_psf(parser, args):
    wmap, mask, rms, inputs, pupil = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad, pupil_diameter_px=2*pupil["radius_px"])
    results = {"strehl": res["strehl"], "rms_waves": rms, "fwhm_lambda_fnum": res["fwhm_lambda_fnum"],
               "encircled_energy_airy": res["encircled_energy_airy"], "pixel_lambda_fnum": res["pixel_lambda_fnum"]}
    units = {"rms_waves": "waves", "fwhm_lambda_fnum": "lambda*F#", "pixel_lambda_fnum": "lambda*F#"}
    _pupil_results(results, units, pupil)
    _physical(results, units, args)
    warnings = _model_warnings(args)
    results["strehl_reference"] = "sampled_peak_same_pupil_zero_phase"
    results["strehl_exponential_estimate"] = float(np.exp(-(2*np.pi*rms)**2))
    results["strehl_approximation_status"] = "small_error_estimate_not_a_consistency_test"
    if args.out:
        np.save(args.out, res["psf"])
        results["psf_file"] = args.out
    method = "Scalar Fraunhofer PSF = |FFT(P·exp(2πiW))|²; uniform pupil amplitude; Strehl = sampled peak / same-pupil zero-phase peak; F# uses the normalization diameter; zero-padded ×pad (Goodman, Fourier Optics ch. 6). Exponential Strehl is an approximation, not a coefficient-convention test. Airy radius/energy region uses the clear-circle first zero."
    if args.map:
        method += "; piston and tilt removed from map input"
    return cli.Envelope(TOOL, "psf", 0, inputs={**inputs, "pad": args.pad, "wavelength_um": args.wavelength_um, "fnum": args.fnum},
                        results=results, units=units, warnings=warnings, method=method)


def cmd_mtf(parser, args):
    wmap, mask, rms, inputs, pupil = _wavefront(parser, args, args.npix)
    res = fourier.psf_from_wavefront(wmap, mask, pad=args.pad, pupil_diameter_px=2*pupil["radius_px"])
    nu, mx, my = fourier.mtf_from_psf(res["psf"], res["pixel_lambda_fnum"])
    _, ideal_x, ideal_y = fourier.mtf_from_psf(res["ideal_psf"], res["pixel_lambda_fnum"])
    results = {"strehl": res["strehl"], "rms_waves": rms, "ideal_reference": "same_pupil_zero_phase",
               "strehl_reference": "sampled_peak_same_pupil_zero_phase", "pixel_lambda_fnum": res["pixel_lambda_fnum"]}
    units = {"rms_waves": "waves", "pixel_lambda_fnum": "lambda*F#"}
    _pupil_results(results, units, pupil)
    warnings = _model_warnings(args)
    freqs = cli.parse_floats(args.freqs) if args.freqs else []
    if any(f < 0 for f in freqs):
        parser.error("MTF frequencies must be nonnegative")
    if (freqs or args.pixel_um is not None) and args.wavelength_um is None:
        parser.error("--freqs/--pixel-um require --wavelength-um and --fnum")
    if args.wavelength_um is not None and args.fnum is not None:
        cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
        results["cutoff_cyc_per_mm"] = cutoff
        units["cutoff_cyc_per_mm"] = "cyc/mm"
        if args.pixel_um is not None:
            nyq = 1000.0 / (2 * args.pixel_um)
            results["nyquist_cyc_per_mm"] = nyq
            units["nyquist_cyc_per_mm"] = "cyc/mm"
            freqs.append(nyq)
        results["mtf_at"] = {}
        for f in freqs:
            x = f / cutoff
            results["mtf_at"][f"{f:g}"] = {"x": float(np.interp(x, nu, mx, right=0)), "y": float(np.interp(x, nu, my, right=0)),
                                           "ideal_x": float(np.interp(x, nu, ideal_x, right=0)),
                                           "ideal_y": float(np.interp(x, nu, ideal_y, right=0)),
                                           "diffraction_limit": optics.mtf_diffraction(x)}
    if np.any(mx > ideal_x + 1e-10) or np.any(my > ideal_y + 1e-10):
        warnings.append("MTF exceeds the matched phase-free pupil: investigate numerical error")
    results["curve_nu_over_cutoff"] = nu[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_x"] = mx[::max(1, len(nu) // 50)].tolist()
    results["curve_mtf_y"] = my[::max(1, len(nu) // 50)].tolist()
    results["curve_ideal_mtf_x"] = ideal_x[::max(1, len(nu) // 50)].tolist()
    results["curve_ideal_mtf_y"] = ideal_y[::max(1, len(nu) // 50)].tolist()
    method = "Scalar incoherent MTF = |FFT(PSF)| normalized; bound is the matched pupil with zero phase. Legacy diffraction_limit is the clear-circle reference (2/π)(acos x − x√(1−x²)); x = ν λ F# using the normalization diameter (Smith ch. 11)."
    if args.map:
        method += "; piston and tilt removed from map input"
    return cli.Envelope(TOOL, "mtf", 0, inputs={**inputs, "pad": args.pad, "wavelength_um": args.wavelength_um, "fnum": args.fnum, "pixel_um": args.pixel_um, "freqs": args.freqs},
                        results=results, units=units, warnings=warnings, method=method)


def cmd_sample_check(parser, args):
    q = optics.sampling_q(args.wavelength_um, args.fnum, args.pixel_um)
    cutoff = optics.mtf_cutoff_cyc_per_mm(args.wavelength_um, args.fnum)
    nyq = 1000.0 / (2 * args.pixel_um)
    warnings = []
    if q < 2:
        warnings.append(f"Q = {q:.2f} < 2: detector Nyquist ({nyq:.1f} cyc/mm) is below the scalar incoherent optical cutoff ({cutoff:.1f} cyc/mm); aliasing risk depends on scene content")
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
        sub.add_argument("--wavelength-um", type=cli.positive_float)
        sub.add_argument("--fnum", type=cli.positive_float)
        sub.add_argument("--npix", type=int, help="pupil samples across (coefficient input only; default 128)")
        sub.add_argument("--pad", type=int, default=8, help="FFT zero-padding factor")
        sub.add_argument("--pupil-center-px", help="explicit map normalization-circle row,col in sample coordinates")
        sub.add_argument("--pupil-radius-px", type=cli.positive_float, help="explicit map normalization radius in sample intervals")

    def psf(sub):
        source(sub)
        sub.add_argument("--out", help="save the normalized PSF grid as .npy")
    add("psf", "PSF, Strehl, FWHM and encircled energy from a wavefront", "psf --scheme fringe --coeffs 0,0,0,0.125 --wavelength-um 0.55 --fnum 4", cmd_psf, psf)

    def mtf(sub):
        source(sub)
        sub.add_argument("--pixel-um", type=cli.positive_float, help="detector pitch, adds MTF at Nyquist")
        sub.add_argument("--freqs", help="comma list of cyc/mm to report")
    add("mtf", "MTF curve with diffraction-limit comparison", "mtf --scheme noll --coeffs 0 --wavelength-um 0.5 --fnum 4 --pixel-um 5 --freqs 50,100", cmd_mtf, mtf)

    def sample(sub):
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--fnum", type=cli.positive_float, required=True)
        sub.add_argument("--pixel-um", type=cli.positive_float, required=True)
    add("sample-check", "Detector sampling Q vs. optical cutoff", "sample-check --wavelength-um 0.5 --fnum 4 --pixel-um 1", cmd_sample_check, sample)
    return parser


def main(argv: list[str] | None = None) -> int:
    return cli.run(build_parser, argv)


if __name__ == "__main__":
    sys.exit(main())
