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
    try:
        phase = psi_phase(frames, args.algorithm)
    except ValueError as e:
        parser.error(str(e))
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
    phase = load_map(args.phase)
    wfe = phase / (2 * math.pi) / args.passes
    results = {"passes": args.passes}
    units = {}
    pupil = None
    if args.nterms:
        coeffs, resid, pupil = fit_map(wfe, args.scheme, args.nterms)
        low = [c if (n, m) in LOW_ORDER else 0.0 for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs)))]
        rho, theta, _circle = pupil_grid(wfe.shape, pupil)
        wfe = wfe - np.tensordot(np.asarray(low), Z.basis(args.scheme, len(low), rho, theta), axes=1)
        results.update({"coefficients": coeffs, "terms": terms(args.scheme, coeffs), "scheme": args.scheme,
                        "rms_waves": rms_from_coeffs(args.scheme, coeffs), "fit_residual_rms_waves": resid,
                        "normalization_radius_px": pupil["radius_px"], "pupil_center_px": pupil["center_px"]})
        units.update({"rms_waves": "waves", "fit_residual_rms_waves": "waves",
                      "normalization_radius_px": "px", "pupil_center_px": "px (row, col)"})
    # PV and map RMS are pupil quantities: a full square carries no NaN boundary, so the
    # fitted circle (inscribed circle when no fit ran) bounds them instead of the canvas.
    circle = pupil_grid(wfe.shape, pupil)[2] if pupil else Z.unit_disk(wfe.shape[0])[2]
    valid = circle & np.isfinite(wfe)
    results["pv_waves"] = float(np.max(wfe[valid]) - np.min(wfe[valid]))
    results["rms_map_waves"] = float(np.sqrt(np.mean((wfe[valid] - wfe[valid].mean()) ** 2)))
    units.update({"pv_waves": "waves", "rms_map_waves": "waves"})
    if args.out:
        np.save(args.out, wfe)
        results["wfe_file"] = args.out
    return cli.Envelope(TOOL, "fringe-to-wfe", 0, inputs={"phase": args.phase, "passes": args.passes, "scheme": args.scheme, "nterms": args.nterms},
                        results=results, units=units,
                        method="W = φ/(2π)/passes (passes=2 for Fizeau/Twyman-Green reflection tests); piston/tilt removed after Zernike fit; PV and map RMS over the pupil circle only")


def cmd_cavity(parser, args):
    lam_mm = args.wavelength_um * 1e-3
    results = {"opd_mm": 2 * args.gap_mm}
    units = {"opd_mm": "mm"}
    warnings = []
    if args.tilt_arcsec is not None:
        theta = math.radians(args.tilt_arcsec / 3600)
        results["fringe_spacing_mm"] = lam_mm / (2 * math.tan(theta))
        results["fringes_across_100mm"] = 100.0 / results["fringe_spacing_mm"]
        units["fringe_spacing_mm"] = "mm"
    if args.linewidth_nm is not None:
        lc = (args.wavelength_um ** 2) / (args.linewidth_nm * 1e-3) * 1e-3  # µm²/µm -> µm -> mm
        results["coherence_length_mm"] = lc
        units["coherence_length_mm"] = "mm"
        results["opd_over_coherence_length"] = results["opd_mm"] / lc
        if results["opd_over_coherence_length"] > 0.5:
            warnings.append("cavity OPD exceeds half the coherence length: fringe contrast will collapse")
    return cli.Envelope(TOOL, "cavity", 0,
                        inputs={"gap_mm": args.gap_mm, "wavelength_um": args.wavelength_um, "tilt_arcsec": args.tilt_arcsec, "linewidth_nm": args.linewidth_nm},
                        results=results, units=units, warnings=warnings,
                        method="Double-pass cavity: OPD = 2·gap; tilt fringe spacing λ/(2 tan θ); coherence length λ²/Δλ (Malacara ch. 1)")


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
        sub.add_argument("--passes", type=int, default=2)
        sub.add_argument("--scheme", choices=Z.SCHEMES, default="fringe")
        sub.add_argument("--nterms", type=int, default=37)
        sub.add_argument("--out")
    add("fringe-to-wfe", "Phase map to wavefront error, with Zernike fit", "fringe-to-wfe --phase unwrapped.npy --passes 2 --nterms 37", cmd_fringe_to_wfe, f2w)

    def cavity(sub):
        sub.add_argument("--gap-mm", type=float, required=True)
        sub.add_argument("--wavelength-um", type=float, required=True)
        sub.add_argument("--tilt-arcsec", type=float)
        sub.add_argument("--linewidth-nm", type=float)
    add("cavity", "Fizeau/Twyman-Green cavity OPD, tilt fringes, coherence check", "cavity --gap-mm 5 --wavelength-um 0.6328 --tilt-arcsec 10 --linewidth-nm 0.001", cmd_cavity, cavity)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
