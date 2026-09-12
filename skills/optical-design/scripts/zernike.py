# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Zernike coefficient tools: convert schemes, RMS/PV, Strehl, Seidel from Fringe, fit a map (Tier 0)."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import cli  # noqa: E402, RUF100
from _lib import zernike as Z  # noqa: E402, RUF100

TOOL = "zernike"
LOW_ORDER = {(0, 0), (1, 1), (1, -1)}


def coefficients_to_map(scheme: str, coeffs: list[float], npix: int = 256):
    rho, theta, mask = Z.unit_disk(npix)
    B = Z.basis(scheme, len(coeffs), rho, theta)
    wmap = np.tensordot(np.asarray(coeffs, float), B, axes=1)
    wmap[~mask] = np.nan
    return wmap, mask


def rms_from_coeffs(scheme: str, coeffs: list[float], exclude_low_order: bool = True) -> float:
    total = 0.0
    for c, (n, m) in zip(coeffs, Z.indices(scheme, len(coeffs))):
        if exclude_low_order and (n, m) in LOW_ORDER:
            continue
        total += (c / Z.norm("noll", n, m)) ** 2 if scheme == "fringe" else c * c
    return math.sqrt(total)


def _terms(scheme: str, coeffs: list[float]):
    j0 = Z.first_index(scheme)
    return [{"j": j0 + i, "n": n, "m": m, "name": Z.name(n, m), "value": c}
            for i, (c, (n, m)) in enumerate(zip(coeffs, Z.indices(scheme, len(coeffs))))]


def _default_nterms(dst: str, coeffs: list[float], src_idx: list[tuple[int, int]]) -> int:
    """Smallest destination term count covering every (n, m) with a nonzero source
    coefficient, never less than len(coeffs). Searches a generous bound of destination
    indices (37 is the whole fringe scheme; 400 comfortably covers noll/ansi radial orders)."""
    needed = {nm for c, nm in zip(coeffs, src_idx) if c != 0.0}
    bound = 37 if dst == "fringe" else 400
    dst_bound_idx = Z.indices(dst, bound)
    covering = 0
    for nm in needed:
        if nm in dst_bound_idx:
            covering = max(covering, dst_bound_idx.index(nm) + 1)
    nterms = max(len(coeffs), covering, 1)
    if dst == "fringe":
        nterms = min(nterms, 37)
    return nterms


def cmd_convert(parser, args):
    src, dst = args.from_scheme, args.to_scheme
    coeffs = cli.parse_floats(args.coeffs)
    src_idx = Z.indices(src, len(coeffs))
    nterms = args.nterms or _default_nterms(dst, coeffs, src_idx)
    dst_idx = Z.indices(dst, nterms)
    lookup = {nm: i for i, nm in enumerate(dst_idx)}
    out = [0.0] * len(dst_idx)
    warnings = []
    for c, nm in zip(coeffs, src_idx):
        if c == 0.0:
            continue
        if nm in lookup:
            n, m = nm
            out[lookup[nm]] = c * Z.norm(src, n, m) / Z.norm(dst, n, m)
        else:
            warnings.append(f"dropped {Z.name(*nm)} {nm}: not within {nterms} terms of {dst}")
    return cli.Envelope(TOOL, "convert", 0,
                        inputs={"from": src, "to": dst, "coefficients": coeffs, "nterms": nterms},
                        results={"coefficients": out, "terms": _terms(dst, out), "scheme": dst},
                        units={"coefficients": "waves (same unit as input)"},
                        method="Same wavefront in both schemes: c_dst = c_src · N_src/N_dst, matched by (n, m); "
                               "Fringe N=1, Noll/ANSI N=√(n+1) (m=0) or √(2(n+1)) (Wyant & Creath 1992; Noll 1976; ANSI Z80.28)",
                        warnings=warnings)


def cmd_rms(parser, args):
    coeffs = cli.parse_floats(args.coeffs)
    rms = rms_from_coeffs(args.scheme, coeffs, exclude_low_order=not args.include_low_order)
    wmap, _mask = coefficients_to_map(args.scheme, coeffs, npix=256)
    if not args.include_low_order:
        low = [c if (n, m) in LOW_ORDER else 0.0 for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs)))]
        wmap -= coefficients_to_map(args.scheme, low, npix=256)[0]
    pv = float(np.nanmax(wmap) - np.nanmin(wmap))
    contributions = [{"name": Z.name(n, m), "rms": abs(c) / Z.norm("noll", n, m) if args.scheme == "fringe" else abs(c)}
                     for c, (n, m) in zip(coeffs, Z.indices(args.scheme, len(coeffs))) if c != 0.0]
    return cli.Envelope(TOOL, "rms", 0,
                        inputs={"scheme": args.scheme, "coefficients": coeffs, "include_low_order": args.include_low_order},
                        results={"rms_waves": rms, "pv_waves": pv, "per_term_rms": contributions},
                        units={"rms_waves": "waves", "pv_waves": "waves"},
                        method="RMS = √Σ(c_j/N_j)² over the unit disk (orthogonality); piston and tilt excluded unless --include-low-order; PV sampled on 256² grid (Noll 1976; Wyant & Creath 1992)")


def load_map(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() == ".npy":
        return np.load(p).astype(float)
    return np.loadtxt(p, delimiter=",").astype(float)


def fit_map(wmap: np.ndarray, scheme: str, nterms: int, mask: np.ndarray | None = None):
    """Least-squares Zernike fit on the inscribed unit disk; NaN samples are ignored."""
    npix = wmap.shape[0]
    if wmap.shape[0] != wmap.shape[1]:
        raise ValueError("map must be square (pupil inscribed)")
    rho, theta, disk = Z.unit_disk(npix)
    valid = disk & np.isfinite(wmap)
    if mask is not None:
        valid &= mask.astype(bool)
    B = Z.basis(scheme, nterms, rho, theta)
    A = B[:, valid].T
    y = wmap[valid]
    coeffs, *_ = np.linalg.lstsq(A, y, rcond=None)
    residual = y - A @ coeffs
    return [float(c) for c in coeffs], float(np.sqrt(np.mean(residual**2)))


def strehl_pair(rms_waves: float) -> tuple[float, float]:
    phase = 2 * math.pi * rms_waves
    return 1.0 - phase**2, math.exp(-(phase**2))


def cmd_strehl(parser, args):
    if args.rms_waves is None and args.coeffs is None:
        parser.error("give --rms-waves or --scheme with --coeffs")
    rms = args.rms_waves if args.rms_waves is not None else rms_from_coeffs(args.scheme, cli.parse_floats(args.coeffs))
    marechal, extended = strehl_pair(rms)
    warnings = []
    if rms > 0.1:
        warnings.append("RMS > 0.1 waves: Maréchal approximation not valid; compute the PSF (wavefront.py psf) instead")
    return cli.Envelope(TOOL, "strehl", 0,
                        inputs={"rms_waves": rms, "scheme": args.scheme, "coefficients": args.coeffs},
                        results={"rms_waves": rms, "strehl_marechal": marechal, "strehl_extended": extended,
                                 "meets_marechal_criterion": rms <= 1 / 14},
                        units={"rms_waves": "waves"},
                        method="Maréchal S ≈ 1 − (2πσ)²; extended S ≈ exp(−(2πσ)²); diffraction-limited when σ ≤ λ/14 (S ≥ 0.8) (Born & Wolf §9.3; Mahajan 1983)",
                        warnings=warnings)


def cmd_seidel(parser, args):
    z = cli.parse_floats(args.coeffs)
    if len(z) < 9:
        parser.error("seidel-from-zernike needs at least 9 Fringe coefficients (Z1..Z9)")
    _Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9 = z[:9]
    astig = 2 * math.hypot(Z5, Z6)
    coma = 3 * math.hypot(Z7, Z8)
    sph = 6 * Z9
    return cli.Envelope(TOOL, "seidel-from-zernike", 0,
                        inputs={"scheme": "fringe", "coefficients": z[:9]},
                        results={
                            "tilt_waves": math.hypot(Z2 - 2 * Z7, Z3 - 2 * Z8),
                            "tilt_angle_deg": math.degrees(math.atan2(Z3 - 2 * Z8, Z2 - 2 * Z7)),
                            "defocus_w020_waves": 2 * Z4 - 6 * Z9,
                            "astigmatism_w222_waves": astig,
                            "astigmatism_angle_deg": 0.5 * math.degrees(math.atan2(Z6, Z5)),
                            "coma_w131_waves": coma,
                            "coma_angle_deg": math.degrees(math.atan2(Z8, Z7)),
                            "spherical_w040_waves": sph,
                        },
                        units={k: "waves" for k in ("tilt_waves", "defocus_w020_waves", "astigmatism_w222_waves", "coma_w131_waves", "spherical_w040_waves")},
                        method="Wyant & Creath 1992, 'Basic Wavefront Aberration Theory for Optical Metrology', Table 3, "
                               "Fringe (unnormalized) coefficients: W040=6Z9, W131=3√(Z7²+Z8²), W222=2√(Z5²+Z6²), "
                               "W020=2Z4−6Z9 (add ±W222/2 to reach the sagittal/tangential foci), tilt=√((Z2−2Z7)²+(Z3−2Z8)²)")


def cmd_fit(parser, args):
    wmap = load_map(args.map)
    coeffs, resid = fit_map(wmap, args.scheme, args.nterms)
    return cli.Envelope(TOOL, "fit", 0,
                        inputs={"map": args.map, "scheme": args.scheme, "nterms": args.nterms, "shape": list(wmap.shape)},
                        results={"coefficients": coeffs, "terms": _terms(args.scheme, coeffs), "residual_rms_waves": resid,
                                 "rms_waves": rms_from_coeffs(args.scheme, coeffs)},
                        units={"coefficients": "map units", "residual_rms_waves": "map units", "rms_waves": "map units"},
                        method="Linear least squares on the inscribed unit disk; NaN samples excluded; RMS excludes piston/tilt")


def build_parser() -> argparse.ArgumentParser:
    common = cli.common_parser()
    parser = argparse.ArgumentParser(prog="zernike.py", description=__doc__)
    subs = parser.add_subparsers(dest="subcommand", required=True)

    def add(name, help_, example, func, configure):
        sub = subs.add_parser(name, parents=[common], help=help_, description=help_, epilog=f"example: uv run zernike.py {example}")
        configure(sub)
        sub.set_defaults(func=func, sub=sub)

    def convert(sub):
        sub.add_argument("--from", dest="from_scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--to", dest="to_scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--coeffs", required=True, help="comma list or file; ordered by the source scheme starting at its first index")
        sub.add_argument("--nterms", type=int, help="terms in the output (default: enough to hold the input)")
    add("convert", "Convert coefficients between fringe, noll and ansi schemes", "convert --from fringe --to noll --coeffs 0,0,0,0.25", cmd_convert, convert)

    def rms(sub):
        sub.add_argument("--scheme", choices=Z.SCHEMES, required=True)
        sub.add_argument("--coeffs", required=True)
        sub.add_argument("--include-low-order", action="store_true", help="keep piston and tilt")
    add("rms", "RMS and PV wavefront error from coefficients", "rms --scheme fringe --coeffs 0,0,0,0.25", cmd_rms, rms)

    def strehl(sub):
        sub.add_argument("--rms-waves", type=float)
        sub.add_argument("--scheme", choices=Z.SCHEMES)
        sub.add_argument("--coeffs")
    add("strehl", "Strehl ratio from RMS wavefront error or coefficients", "strehl --rms-waves 0.0714", cmd_strehl, strehl)

    def seidel(sub):
        sub.add_argument("--coeffs", required=True, help="Fringe coefficients Z1..Z9 (or more) in waves")
    add("seidel-from-zernike", "Seidel-type aberration magnitudes from Fringe coefficients", "seidel-from-zernike --coeffs 0,0,0,0,0.05,0,0.1,0,0.2", cmd_seidel, seidel)

    def fit(sub):
        sub.add_argument("--map", required=True, help=".npy or .csv square wavefront map, NaN outside the pupil")
        sub.add_argument("--scheme", choices=Z.SCHEMES, default="fringe")
        sub.add_argument("--nterms", type=int, default=37)
    add("fit", "Least-squares Zernike fit of a wavefront map", "fit --map wfe.npy --scheme fringe --nterms 37", cmd_fit, fit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
