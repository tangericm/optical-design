"""Conservative, shared assessment of the Optiland 0.6.2 import boundary.

Parsing success is not a fidelity guarantee. Categories describe the importer,
not whether a source directive matters to its original optical model.
"""
from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

PRESERVED = {
    "SURF", "TYPE", "CURV", "DISZ", "GLAS", "CONI", "PARM", "STOP",
    "ENPD", "FTYP", "XFLN", "YFLN", "WAVM", "PWAV", "GCAT", "FNUM", "OBNA",
    "UNIT", "MODE", "FWGN", "FLOA", "CLAP", "VCXN", "VCYN",
}
DISPLAY_METADATA = {"AUTH", "NAME", "NOTE", "VERS", "SSID", "LUID", "LANG", "HIDE", "PICB"}
UNSUPPORTED_OPTICAL = {
    "MEMA", "FLAP", "POPS", "RAIM", "POLS", "ENVD", "GFAC", "DIAM",
    "GSTD", "GLRS", "COFN", "MNUM", "MOFF", "NSCD",
}
KNOWN_SURFACE_TYPES = {"STANDARD", "EVENASPH", "PARAXIAL", "ODDASPHE"}


def decode_zmx_text(raw: bytes) -> str:
    # BOM-less ASCII can decode as nonsense UTF-16 when its byte count is even.
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    if b"\x00" in raw[:100]:
        return raw.decode("utf-16-le")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeError:
        return raw.decode("iso-8859-1")


def classify(key: str) -> str:
    if key in PRESERVED:
        return "preserved"
    if key in DISPLAY_METADATA:
        return "display_metadata"
    if key in UNSUPPORTED_OPTICAL or key.startswith(("VD", "VC", "VAN", "TOL", "NSC")):
        return "unsupported_optical"
    return "unknown"


def assess_model(model_path: str | Path, raw: bytes | None = None) -> dict:
    """Return JSON-safe fidelity data, usable without loading an optical engine.

Native JSON lengths follow Optiland's mm convention. ZMX files with non-mm or
unspecified units may be inspected but must be explicitly converted before
millimetre numerical analysis. Unsupported/unknown ZMX content remains visible
even if a calculation on the imported approximation is possible.
"""
    path = Path(model_path)
    if path.suffix.lower() not in {".zmx", ".json"}:
        raise ValueError(f"unsupported model file extension {path.suffix!r}: expected .zmx or .json")
    assessment = {"status": "preserved", "source_units": "mm",
                  "numerical_analysis_allowed": True, "warnings": []}
    if path.suffix.lower() == ".json":
        return assessment
    text = decode_zmx_text(raw if raw is not None else path.read_bytes())
    rows = [line.split() for line in text.splitlines() if line.split()]
    keys = list(dict.fromkeys(row[0] for row in rows))
    declared_units = [row[1].upper() for row in rows if row[0] == "UNIT" and len(row) > 1]
    unit = declared_units[0] if len(set(declared_units)) == 1 else None
    assessment["source_units"] = "mm" if unit == "MM" else unit or "unspecified"
    warnings = assessment["warnings"]
    if unit != "MM":
        assessment["numerical_analysis_allowed"] = False
        warnings.append(f"file declares UNIT {unit or 'unspecified/ambiguous'}; convert the prescription "
                        "explicitly to UNIT MM before numerical analysis: Optiland 0.6.2 does not "
                        "convert non-millimetre lengths; inspection reports raw file values")
    directives = [{"key": key, "category": classify(key), "used": classify(key) == "preserved"}
                  for key in keys]
    if "FLOA" in keys:
        for directive in directives:
            if directive["key"] == "DIAM":
                directive.update(category="preserved", used=True)
    assessment["directives"] = directives
    unsupported = [d["key"] for d in directives if d["category"] == "unsupported_optical"]
    unknown = [d["key"] for d in directives if d["category"] == "unknown"]
    if unsupported:
        warnings.append("Unsupported directives with possible optical effect: " + ", ".join(unsupported)
                        + "; source settings are not certified as preserved (including aperture/clipping, "
                        "vignetting, polarization and ray aiming)")
    if unknown:
        warnings.append("Unknown directives: " + ", ".join(unknown)
                        + "; optical relevance has not been established")
    for row in rows:
        if row[0] == "MNUM" and len(row) > 1:
            try:
                count = int(row[1])
            except ValueError:
                continue
            if count > 1:
                warnings.append(f"file declares {count} configurations; only the loaded default "
                                "configuration is represented")
        if row[0] == "TYPE" and len(row) > 1 and row[1] not in KNOWN_SURFACE_TYPES:
            warnings.append(f"TYPE {row[1]} is outside the supported centered surface set; "
                            "verify the intended geometry and coordinate transformations")
        if row[0] == "MODE" and len(row) > 1 and row[1] != "SEQ":
            warnings.append(f"MODE {row[1]} is not a supported sequential prescription")
    if any(key.startswith("NSC") and key != "NSCD" for key in keys):
        warnings.append("non-sequential component geometry is not represented")
    if warnings:
        assessment["status"] = "partial"
    return assessment


def load_assessed_model(model_path: str | Path, *, allow_raw_units: bool = False,
                        raw: bytes | None = None):
    """Load while retaining engine diagnostics in JSON-safe assessment data."""
    from optiland.fileio import load_optiland_file, load_zemax_file

    path = Path(model_path)
    assessment = assess_model(path, raw)
    if not allow_raw_units and not assessment["numerical_analysis_allowed"]:
        raise ValueError(assessment["warnings"][0])
    engine_output = io.StringIO()
    with redirect_stdout(engine_output):
        optic = (load_optiland_file(str(path)) if path.suffix.lower() == ".json"
                 else load_zemax_file(str(path)))
    for line in engine_output.getvalue().splitlines():
        if line.strip():
            assessment["warnings"].append("Optiland importer: " + line.strip())
            assessment["status"] = "partial"
    optic._import_fidelity = assessment
    return optic, assessment
