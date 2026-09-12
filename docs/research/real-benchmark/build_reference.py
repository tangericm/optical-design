"""Build immutable comparison inputs from saved evidence; never run an optical engine.

Run with Python from any directory. Writes only sibling reference.json and
manifest.json. Source arrays remain absolute irradiance (POP) or the saved native
normalized intensity (Huygens). Provenance/limitations: reference-audit.md.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

SOURCE = Path("C:/Users/erict/OneDrive/Desktop/Projects/ZEMAX/Line-Field-OCT-Optics")
OUTPUT = Path(__file__).resolve().parent
MODEL_IDS = ("Stock", "IdealSurrogate", "FlatPlate")
EXPECTED_RAW = {
    "final-planar-huygens.jsonl": "dd2e02d75ddaf3806f8f52bee0f5e693f874ee22b5e71f1fbf1b808910046184",
    "final-planar-pop.jsonl": "efbb5dfacf31ee8f8313363d43ec4291485852a16f5289b236cf2af767834d2d",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(name):
    path = SOURCE / "reports/evidence" / name
    if sha256(path) != EXPECTED_RAW[name]:
        raise ValueError(f"Source evidence hash changed: {name}")
    return [json.loads(line) for line in path.read_text().splitlines()]


def profile(x_mm, intensity):
    if len(x_mm) != len(intensity) or len(x_mm) < 2:
        raise ValueError("Reference coordinate/intensity lengths must match")
    if not all(math.isfinite(v) for v in x_mm + intensity):
        raise ValueError("Nonfinite source profile")
    if not all(a < b for a, b in zip(x_mm, x_mm[1:])):
        raise ValueError("Source coordinates must increase")
    return {"x_mm": x_mm, "intensity": intensity}


def huygens_case(row):
    return {
        "id": f"huygens_{row['axis'].lower()}_w{row['wave_number']}_p{row['pupil']}_i{row['image']}",
        "method": "huygens", "field": 1, "wavelength": row["wave_number"],
        "polarization": True, "axis": row["axis"].lower(),
        "pupil": row["pupil"], "image": row["image"],
        "delta_um": row["delta_um"], "reference": row["method"],
    }


def pop_case(row):
    waist = (4.6 + (row["wave"] - 0.780) * 0.4 / 0.070) * 0.001 / 2
    return {
        "id": f"pop_w{row['wave_number']}_n{row['n']}",
        "method": "pop", "field": 1, "wavelength": row["wave_number"],
        "polarization": True, "sampling": row["n"],
        "window_mm": 0.4 if row["stage"] == "SLD_POP" else row["window"],
        "waist_x_mm": waist, "waist_y_mm": waist,
        "start_surface": 1, "end_surface": 28, "power_w": 1,
        "separate_xy": True,
        "resampling": [{"surface": s, "width_mm": w} for s, w in ((4, 8), (15, 64), (24, 64))],
    }


def build():
    # Loading the pure validator cannot launch an engine; prevent bytecode writes.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(OUTPUT.parents[2] / "skills/optical-design/scripts"))
    from _lib.profile_benchmark import validate_case

    source_models = json.loads((SOURCE / "source/full_sample/models.json").read_text())
    models = []
    for model_id in MODEL_IDS:
        model = next(m for m in source_models if m["variant"] == model_id)
        path = SOURCE / model["file"]
        if sha256(path) != model["sha256"]:
            raise ValueError(f"Model hash changed: {model_id}")
        header = path.read_text(encoding="utf-16")
        active = re.search(r"(?m)^FTYP\s+\S+\s+\S+\s+\S+\s+(\d+)", header)
        if not active or int(active[1]) != 18:
            raise ValueError("Expected exactly 18 active wavelengths")
        models.append({"id": model_id, "path": path.as_posix(), "sha256": model["sha256"]})

    hrows = read_rows("final-planar-huygens.jsonl")
    prows = read_rows("final-planar-pop.jsonl")
    if len(hrows) != 15 or len(prows) != 60:
        raise ValueError("Unexpected saved case count")
    cases, records = {}, []
    for model_id in MODEL_IDS:
        selected_h = [r for r in hrows if r["variant"] == model_id]
        selected_p = [r for r in prows if r["variant"] == model_id]
        if len(selected_h) != 5 or len(selected_p) != 20:
            raise ValueError("Expected five Huygens and twenty POP cases per model")
        for row in selected_h + selected_p:
            is_h = row["kind"] == "Huygens"
            case = validate_case(huygens_case(row) if is_h else pop_case(row))
            case_id = case["id"]
            if case_id in cases and cases[case_id] != case:
                raise ValueError("Shared case settings differ across models")
            cases[case_id] = case
            if is_h:
                if not row["valid"] or row["series"] != 1 or row["grids"] != 0:
                    raise ValueError("Invalid Huygens source record")
                profiles = {case["axis"]: profile([v / 1000 for v in row["x"]], row["y"])}
            else:
                if row["kind"] != "POP" or row["messages"]:
                    raise ValueError("Unexpected POP messages/type")
                profiles = {}
                for axis in ("x", "y"):
                    if len(row[axis]) != row["n" + axis]:
                        raise ValueError("POP cut length differs from native grid dimension")
                    # Saved x/y are the native nearest-zero row/column cuts.
                    # They are irradiance samples, NOT coordinate arrays.
                    coords = [row[axis + "0"] + i * row["d" + axis] for i in range(len(row[axis]))]
                    profiles[axis] = profile(coords, row[axis])
                central_y = next(c for c in row["ycuts"] if c["requested_x"] == 0)
                if central_y["y"] != row["y"]:
                    raise ValueError("Saved central Y disagrees with the zero-X local cut")
            record = {"model_id": model_id, "case_id": case_id, "profiles": profiles}
            if not is_h:
                if not math.isfinite(row["power"]) or row["power"] <= 0:
                    raise ValueError("Invalid integrated POP power")
                record["power_w"] = row["power"]
            records.append(record)
    if len(cases) != 25 or len(records) != 75:
        raise ValueError("Expected 25 shared cases and 75 records")
    expected = {(m, c) for m in MODEL_IDS for c in cases}
    if {(r["model_id"], r["case_id"]) for r in records} != expected:
        raise ValueError("Reference record identities do not cover all models/cases")

    reference_path = OUTPUT / "reference.json"
    reference_path.write_text(json.dumps({"records": records}, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1, "name": "Line-Field OCT saved planar diffraction profiles",
        "models": models, "cases": list(cases.values()),
        "reference": {"path": "reference.json", "sha256": sha256(reference_path)},
        "comparison": {"rtol": 1e-6, "atol": 1e-8},
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(models)} models, {len(cases)} shared cases, {len(records)} reference records")
    print(f"reference SHA-256: {manifest['reference']['sha256']}")


if __name__ == "__main__":
    build()
