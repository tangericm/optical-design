# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "scikit-image>=0.22"]
# ///
"""Phase-shifting interferometry, unwrapping, fringe-to-wavefront, cavity checks (Tier 0)."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib.zernike as Z  # noqa: E402, RUF100
from _lib import cli  # noqa: E402, RUF100
from _lib.wfmap import (  # noqa: E402, RUF100
    LOW_ORDER,
    fit_map,
    load_map,
    pupil_grid,
    rms_from_coeffs,
    terms,
)

TOOL = "interfero"
ALGORITHMS = ("3step", "4step", "5step")


def psi_phase(frames: np.ndarray, algorithm: str) -> np.ndarray:
    """Wrapped phase from N intensity frames (Malacara, Optical Shop Testing, ch. 14).

    3step: steps 0, 2π/3, 4π/3 -> atan2(√3 (I3 − I2), 2 I1 − I2 − I3)
    4step: steps 0, π/2, π, 3π/2 -> atan2(I4 − I2, I1 − I3)
    5step (Hariharan): steps −π, −π/2, 0, π/2, π -> atan2(2 (I2 − I4), 2 I3 − I1 − I5)
    """
    frames = np.asarray(frames)
    if frames.ndim != 3 or min(frames.shape) < 1:
        raise ValueError("frames must have nonempty shape (N, H, W)")
    if not np.issubdtype(frames.dtype, np.number) or np.iscomplexobj(frames):
        raise ValueError("intensity frames must be real numeric arrays")
    if not np.isfinite(frames).all():
        raise ValueError("intensity frames must contain finite values")
    I = [f.astype(float) for f in frames]
    if algorithm == "3step":
        if len(I) != 3:
            raise ValueError("3step needs 3 frames")
        return np.arctan2(math.sqrt(3) * (I[2] - I[1]), 2 * I[0] - I[1] - I[2])
    if algorithm == "4step":
        if len(I) != 4:
            raise ValueError("4step needs 4 frames")
        return np.arctan2(I[3] - I[1], I[0] - I[2])
    if algorithm == "5step":
        if len(I) != 5:
            raise ValueError("5step needs 5 frames")
        return np.arctan2(2 * (I[1] - I[3]), 2 * I[2] - I[0] - I[4])
    raise ValueError(f"unknown algorithm {algorithm}")


def cmd_psi(parser, args):
    frames = np.load(args.frames)
    phase = psi_phase(frames, args.algorithm)   # wrong frame count -> ValueError -> exit 2
    np.save(args.out, phase)
    return cli.Envelope(TOOL, "psi", 0, inputs={"frames": args.frames, "algorithm": args.algorithm, "n_frames": int(frames.shape[0])},
                        results={"phase_file": args.out, "shape": list(phase.shape), "wrapped": True},
                        units={}, method=psi_phase.__doc__.strip().splitlines()[0])


def cmd_unwrap(parser, args):
    skimage = cli.require("skimage.restoration", "install scikit-image (uv run installs it from the script header)")
    wrapped = load_map(args.phase)
    un = np.asarray(skimage.unwrap_phase(np.ma.masked_invalid(wrapped)))
    un = np.where(np.isfinite(wrapped), un, np.nan)
    np.save(args.out, un)
    pv = float(np.nanmax(un) - np.nanmin(un))
    return cli.Envelope(TOOL, "unwrap", 0, inputs={"phase": args.phase},
                        results={"phase_file": args.out, "pv_rad": pv, "pv_waves": pv / (2 * math.pi)},
                        units={"pv_rad": "rad", "pv_waves": "waves"},
                        method="2-D phase unwrapping, Herráez et al. 2002 (scikit-image unwrap_phase)")


def cmd_fringe_to_wfe(parser, args):
    measurement = args.measurement or "single-pass"
    warnings = []
    if args.measurement is None:
        warnings.append("Legacy default assumes inferred single-pass error with additive identical passes; specify --measurement to declare the quantity. Pass count alone does not establish retrace cancellation.")
    if measurement != "single-pass" and args.passes is not None:
        parser.error("--passes applies only to --measurement single-pass")
    if measurement != "surface-height" and args.incidence_deg != 0:
        parser.error("--incidence-deg applies only to --measurement surface-height")
    if not 0 <= args.incidence_deg < 90:
        parser.error("--incidence-deg must be in [0, 90) from the surface normal")
    passes = args.passes if args.passes is not None else 2
    divisor = (passes if measurement == "single-pass" else
               2 * math.cos(math.radians(args.incidence_deg)) if measurement == "surface-height" else 1.0)
    phase = load_map(args.phase)
    measured_opd = phase / (2 * math.pi)
    wfe = measured_opd / divisor
    results = {"passes": passes if measurement == "single-pass" else None,
               "measurement": measurement, "opd_conversion_divisor": divisor,
               "output_quantity": {"single-pass": "inferred single-pass OPD", "measured-opd": "measured OPD",
                                   "surface-height": "inferred reflective surface height"}[measurement],
               "removed_terms": []}
    units = {}
    pupil = None
    if args.nterms:
        coeffs, resid, pupil = fit_map(wfe, args.scheme, args.nterms)
        results["removed_terms"] = [Z.name(n, m) for n, m in Z.indices(args.scheme, args.nterms)
                                    if (n, m) in LOW_ORDER]
        low = [c if (n, m) in LOW_ORDER else 0.0 for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs)))]
        rho, theta, _circle = pupil_grid(wfe.shape, pupil)
        wfe = wfe - np.tensordot(np.asarray(low), Z.basis(args.scheme, len(low), rho, theta), axes=1)
        results.update({"coefficients": coeffs, "terms": terms(args.scheme, coeffs), "scheme": args.scheme,
                        "rms_waves": rms_from_coeffs(args.scheme, coeffs), "fit_residual_rms_waves": resid,
                        "coefficient_full_disk_rms_waves": rms_from_coeffs(args.scheme, coeffs),
                        "fit_rms_on_mask_waves": pupil["fit_rms_on_mask"],
                        "fit_diagnostics": {k: pupil[k] for k in ("rank", "condition_number", "valid_samples", "valid_coverage_fraction", "fit_terms")},
                        "normalization_radius_px": pupil["radius_px"], "pupil_center_px": pupil["center_px"]})
        units.update({"rms_waves": "waves", "fit_residual_rms_waves": "waves",
                      "coefficient_full_disk_rms_waves": "waves", "fit_rms_on_mask_waves": "waves",
                      "coefficients": "waves",
                      "normalization_radius_px": "px", "pupil_center_px": "px (row, col)"})
    # PV and map RMS are pupil quantities: a full square carries no NaN boundary, so the
    # fitted circle (inscribed circle when no fit ran) bounds them instead of the canvas.
    valid = np.isfinite(wfe)
    if pupil:
        valid &= pupil_grid(wfe.shape, pupil)[2]
    elif valid.all():
        valid &= Z.unit_disk(wfe.shape[0])[2]
    if not valid.any():
        raise ValueError("phase map has no valid pupil samples")
    measured = measured_opd[valid]
    results["measured_opd_pv_waves"] = float(np.ptp(measured))
    results["measured_opd_rms_waves"] = float(np.std(measured))
    units.update({"measured_opd_pv_waves": "waves", "measured_opd_rms_waves": "waves"})
    results["pv_waves"] = float(np.max(wfe[valid]) - np.min(wfe[valid]))
    results["rms_map_waves"] = float(np.sqrt(np.mean((wfe[valid] - wfe[valid].mean()) ** 2)))
    units.update({"pv_waves": "waves", "rms_map_waves": "waves"})
    if measurement == "surface-height":
        units.update({k: "wavelengths of surface height" for k in
                      ("pv_waves", "rms_map_waves", "rms_waves", "fit_residual_rms_waves",
                       "coefficient_full_disk_rms_waves", "fit_rms_on_mask_waves", "coefficients") if k in results})
    if args.out:
        np.save(args.out, wfe)
        results["wfe_file"] = args.out
    return cli.Envelope(TOOL, "fringe-to-wfe", 0,
                        inputs={"phase": args.phase, "passes": results["passes"], "scheme": args.scheme,
                                "nterms": args.nterms, "measurement": measurement, "incidence_deg": args.incidence_deg},
                        results=results, units=units, warnings=warnings,
                        method="Measured OPD in waves = φ/(2π), reported before low-order removal. Single-pass inference assumes additive identical pass errors: OPD/passes, without a retrace model. Reflective surface height = OPD/(2 cos incidence), in wavelengths, for a single reflection with known incidence and no other OPD contributors (Malacara, Optical Shop Testing). Legacy *_waves and wfe_file describe output_quantity; fitted low-order terms are removed from output map only. fit_rms_on_mask_waves is reconstructed-map standard deviation before tilt removal; fit_residual_rms_waves is measured-minus-fit RMS. coefficient_full_disk_rms_waves (legacy rms_waves) assumes full-disk orthogonality and excludes piston/tilt; rms_map_waves uses actual valid samples after removed_terms.")


def cmd_cavity(parser, args):
    lam_mm = args.wavelength_um * 1e-3
    results = {"opd_mm": 2 * args.gap_mm}
    units = {"opd_mm": "mm"}
    warnings = []
    if args.tilt_arcsec is not None:
        theta = math.radians(args.tilt_arcsec / 3600)
        if abs(theta) >= math.pi / 2:
            parser.error("--tilt-arcsec must have magnitude below 90 degrees")
        spacing = lam_mm / (2 * abs(math.tan(theta))) if theta else None
        results["fringe_spacing_mm"] = spacing
        results["fringes_across_100mm"] = 100.0 / spacing if spacing else 0.0
        results["tilt_fringe_status"] = "finite_spacing" if theta else "no_tilt_fringes"
        units["fringe_spacing_mm"] = "mm"
    if args.linewidth_nm is not None:
        lc = (args.wavelength_um ** 2) / (args.linewidth_nm * 1e-3) * 1e-3  # µm²/µm -> µm -> mm
        results["coherence_length_mm"] = lc
        units["coherence_length_mm"] = "mm"
        results["opd_over_coherence_length"] = results["opd_mm"] / lc
        results["coherence_length_convention"] = "inverse-bandwidth scale lambda^2/delta_lambda; not a contrast threshold"
        results["contrast_prediction"] = "undetermined_without_spectral_line_shape"
        if results["opd_over_coherence_length"] > 0.5:
            warnings.append("cavity OPD exceeds half the inverse-bandwidth coherence scale; contrast requires spectral line shape and a declared visibility convention")
    return cli.Envelope(TOOL, "cavity", 0,
                        inputs={"gap_mm": args.gap_mm, "wavelength_um": args.wavelength_um, "tilt_arcsec": args.tilt_arcsec, "linewidth_nm": args.linewidth_nm},
                        results=results, units=units, warnings=warnings,
                        method="Normal-incidence cavity in air: OPD = 2·gap; plane-mirror tilt fringe spacing λ/(2 |tan θ|), zero tilt has no finite spacing; coherence length "
                               "λ²/Δλ for a source of linewidth Δλ (Malacara ch. 1). resolve.py oct-axial reports the "
                               "Gaussian-spectrum FWHM coherence length instead, smaller by 2 ln2/π ≈ 0.44")


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="interfero.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run interfero.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def psi(sub):
        sub.add_argument("--frames", required=True, help=".npy stack shaped (N, H, W)")
        sub.add_argument("--algorithm", choices=ALGORITHMS, default="4step")
        sub.add_argument("--out", default="phase_wrapped.npy")
    add("psi", "Wrapped phase from phase-shifted frames", "psi --frames frames.npy --algorithm 4step --out phase.npy", cmd_psi, psi)

    def unwrap(sub):
        sub.add_argument("--phase", required=True)
        sub.add_argument("--out", default="phase_unwrapped.npy")
    add("unwrap", "2-D phase unwrapping", "unwrap --phase phase.npy --out unwrapped.npy", cmd_unwrap, unwrap)

    def f2w(sub):
        sub.add_argument("--phase", required=True,
                         help="unwrapped phase map in radians, NaN outside the pupil, "
                              "or a full square (inscribed circle assumed)")
        sub.add_argument("--measurement", choices=("measured-opd", "single-pass", "surface-height"),
                         help="quantity inferred from phase; omitted retains legacy single-pass assumption")
        sub.add_argument("--passes", type=cli.positive_int, help="identical additive passes for single-pass inference (default 2)")
        sub.add_argument("--incidence-deg", type=cli.finite_float, default=0.0,
                         help="angle from surface normal for reflective surface-height inference (default 0)")
        sub.add_argument("--scheme", choices=Z.SCHEMES, default="fringe")
        sub.add_argument("--nterms", type=cli.nonnegative_int, default=37, help="fit terms; 0 disables fit and low-order removal")
        sub.add_argument("--out")
    add("fringe-to-wfe", "Phase map to wavefront error, with Zernike fit", "fringe-to-wfe --phase unwrapped.npy --passes 2 --nterms 37", cmd_fringe_to_wfe, f2w)

    def cavity(sub):
        sub.add_argument("--gap-mm", type=cli.positive_float, required=True)
        sub.add_argument("--wavelength-um", type=cli.positive_float, required=True)
        sub.add_argument("--tilt-arcsec", type=cli.finite_float)
        sub.add_argument("--linewidth-nm", type=cli.positive_float)
    add("cavity", "Fizeau/Twyman-Green cavity OPD, tilt fringes, coherence check", "cavity --gap-mm 5 --wavelength-um 0.6328 --tilt-arcsec 10 --linewidth-nm 0.001", cmd_cavity, cavity)
    return parser


def main(argv: list[str] | None = None) -> int:
    return cli.run(build_parser, argv)


if __name__ == "__main__":
    sys.exit(main())
