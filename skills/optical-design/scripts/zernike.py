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


def cmd_convert(parser, args):
    src, dst = args.from_scheme, args.to_scheme
    coeffs = cli.parse_floats(args.coeffs)
    src_idx = Z.indices(src, len(coeffs))
    nterms = args.nterms or (37 if dst == "fringe" else max(len(coeffs), 1))
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
                        method="RMS = √Σ(c_j/N_j)² over the unit disk (orthogonality); piston and tilt excluded unless --include-low-order; PV sampled on 256² grid")


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = args.func(args.sub, args)
    cli.emit(env, as_json=args.json)
    return cli.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
