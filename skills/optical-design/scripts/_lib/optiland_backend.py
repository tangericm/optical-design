"""Optiland 0.6.2 adapter for a deliberately restricted sequential imaging subset.

Native Optiland JSON retains its Infinity convention for plane/object geometry.
Reports use string sentinels instead. Models use millimetres and wavelengths in um.
Only centered spherical/plane refractive systems, scalar analyses, EPD aperture,
and meridional angle fields are supported. No solves, pickups or polarization.
"""
from __future__ import annotations

import copy
import json
import math
from importlib.metadata import version
from pathlib import Path

from .design_contract import UNITS, finite, metric_key

VERSION = "0.6.2"
RESTRICTIONS = ("Centered spherical/plane refractive surfaces in air; EPD; meridional angle fields; "
                "millimetres; scalar analysis; no solves, pickups, configurations, coatings, "
                "scattering, apodization or unsupported directives. Catalog glass requires an explicit "
                "catalog and exact material lookup. Native JSON export only.")


def _report_value(value):
    if isinstance(value, dict):
        return {key: _report_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_report_value(child) for child in value]
    if hasattr(value, "tolist"):
        return _report_value(value.tolist())
    if isinstance(value, float) and not math.isfinite(value):
        return "Infinity" if value > 0 else "-Infinity" if value < 0 else "NaN"
    return value


def validate_zemax(path) -> dict:
    """Reject unverified ZMX directives before invoking Optiland's permissive reader."""
    raw = Path(path).read_bytes()
    text = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    allowed = {"VERS", "MODE", "UNIT", "NAME", "NOTE", "ENPD", "FTYP", "XFLN", "YFLN",
               "FWGN", "WAVM", "PWAV", "SURF", "TYPE", "CURV", "DISZ", "GLAS", "GCAT",
               "STOP", "CONI", "COMM"}
    headers, surfaces, waves = {}, [], []
    current = None
    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        key, args = tokens[0], tokens[1:]
        if key not in allowed:
            raise ValueError(f"unsupported Zemax directive: {key}")
        if key == "SURF":
            if len(args) != 1 or int(args[0]) != len(surfaces):
                raise ValueError("unsupported Zemax nonconsecutive surface indices")
            current = {}
            surfaces.append(current)
        elif key in {"TYPE", "CURV", "DISZ", "GLAS", "STOP", "CONI", "COMM"}:
            if current is None or key in current:
                raise ValueError(f"unsupported misplaced or duplicate Zemax {key}")
            current[key] = args
        elif key == "WAVM":
            waves.append(args)
        elif key not in {"NOTE", "VERS", "NAME"}:
            if key in headers:
                raise ValueError(f"unsupported duplicate Zemax {key}")
            headers[key] = args
    try:
        if headers["MODE"] != ["SEQ"] or headers["UNIT"][0] != "MM":
            raise ValueError("unsupported Zemax mode or length unit")
        if not finite(float(headers["ENPD"][0]), "EPD") > 0:
            raise ValueError("unsupported nonpositive EPD")
        ftyp = [int(v) for v in headers["FTYP"]]
        if len(ftyp) != 7 or ftyp[0:2] != [0, 0] or ftyp[4:] != [0, 0, 0]:
            raise ValueError("unsupported Zemax field type, telecentric or afocal settings")
        nf, nw = ftyp[2:4]
        if nf < 1 or nw < 1 or len(waves) != nw:
            raise ValueError("unsupported incomplete Zemax wavelength definitions")
        for key in ("XFLN", "YFLN"):
            values = [finite(float(v), key) for v in headers[key]]
            if len(values) != nf or (key == "XFLN" and any(values)):
                raise ValueError("unsupported Zemax field coordinates")
        if [int(w[0]) for w in waves] != list(range(1, nw + 1)):
            raise ValueError("unsupported Zemax wavelength ordering")
        for wave in waves:
            if len(wave) != 3 or finite(float(wave[1]), "wavelength") <= 0 or finite(float(wave[2]), "weight") < 0:
                raise ValueError("unsupported Zemax wavelength")
        if not 1 <= int(headers["PWAV"][0]) <= nw:
            raise ValueError("unsupported primary wavelength")
        if len(surfaces) < 3 or sum("STOP" in s for s in surfaces[1:-1]) != 1:
            raise ValueError("unsupported Zemax surface/stop definition")
        for index, surface in enumerate(surfaces):
            if surface["TYPE"] != ["STANDARD"]:
                raise ValueError("unsupported Zemax surface type")
            for key in ("CURV", "DISZ", "CONI"):
                if key in surface and len(surface[key]) != 1:
                    raise ValueError(f"unsupported Zemax {key} flags or solves")
            finite(float(surface["CURV"][0]), "curvature")
            distance = surface["DISZ"][0]
            if not (index == 0 and distance == "INFINITY") and finite(float(distance), "thickness") < 0:
                raise ValueError("unsupported negative thickness")
            if "CONI" in surface and float(surface["CONI"][0]) != 0:
                raise ValueError("unsupported Zemax conic/asphere")
            if "GLAS" in surface:
                glass = surface["GLAS"]
                if len(glass) != 3 or glass[1:] != ["0", "0"] or glass[0].upper() == "MIRROR":
                    raise ValueError("unsupported Zemax glass model, solve or mirror")
        if any("GLAS" in surface for surface in surfaces) and len(headers.get("GCAT", [])) != 1:
            raise ValueError("Zemax glass requires exactly one explicit catalog in GCAT")
    except (KeyError, IndexError, OverflowError) as error:
        raise ValueError("unsupported or incomplete Zemax prescription") from error
    return {"format": "Zemax sequential text", "restrictions": RESTRICTIONS,
            "surface_count": len(surfaces), "field_count": nf, "wavelength_count": nw,
            "wavelengths_um": [float(wave[1]) for wave in waves],
            "glass_definitions": [{"surface": index, "name": surface["GLAS"][0],
                                   "catalog": headers["GCAT"][0].lower()}
                                  for index, surface in enumerate(surfaces) if "GLAS" in surface]}


def _exact_catalog_material(data):
    """Ignore permissive saved lookup policy; resolve the declared catalog exactly."""
    from optiland.materials import Material
    catalog = data.get("catalog")
    if not isinstance(catalog, str) or not catalog.strip():
        raise ValueError("catalog glass requires an explicit catalog for exact resolution")
    exact = copy.deepcopy(data)
    exact.update(catalog=catalog.lower(), match_policy="strict", robust_search=None)
    try:
        return Material.from_dict(exact)
    except ValueError as error:
        raise ValueError(f"exact catalog/material lookup failed: {error}") from error


def _material_index(material, wavelength):
    value = material.n(wavelength)
    return finite(float(value.item() if hasattr(value, "item") else value), "refractive index")


def _exact_native_catalogs(data):
    for surface in data["surface_group"]["surfaces"]:
        material = surface["material_post"]
        if material.get("type") == "Material":
            exact = _exact_catalog_material(material)
            for wave in data["wavelengths"]["wavelengths"]:
                _material_index(exact, wave["value"])
            surface["material_post"] = exact.to_dict()


def _validate_native(data):
    try:
        if (data["pickups"] or data["solves"]["solves"] or data.get("apodization")
                or data["wavelengths"]["polarization"] != "ignore"):
            raise ValueError("unsupported native pickups, solves, apodization or polarization")
        if data["aperture"]["type"] != "EPD" or finite(data["aperture"]["value"], "EPD") <= 0:
            raise ValueError("unsupported native aperture; positive EPD required")
        fields = data["fields"]
        if fields["field_definition"]["field_type"] != "AngleField" or fields["telecentric"]:
            raise ValueError("unsupported native field definition")
        if not fields["fields"] or not data["wavelengths"]["wavelengths"]:
            raise ValueError("unsupported empty fields/wavelengths")
        for field in fields["fields"]:
            if field["x"] != 0 or field["vx"] != 0 or field["vy"] != 0:
                raise ValueError("unsupported native nonmeridional/vignetted field")
            finite(field["y"], "field angle")
        for wavelength in data["wavelengths"]["wavelengths"]:
            if wavelength["unit"] != "um" or finite(wavelength["value"], "wavelength") <= 0:
                raise ValueError("unsupported native wavelength units/value")
        surfaces = data["surface_group"]["surfaces"]
        if len(surfaces) < 3 or sum(bool(s.get("is_stop")) for s in surfaces[1:-1]) != 1:
            raise ValueError("unsupported native surface/stop definition")
        for index, surface in enumerate(surfaces):
            geo = surface["geometry"]
            if (surface["type"] != ("ObjectSurface" if index == 0 else "Surface")
                    or geo["type"] not in {"Plane", "StandardGeometry"} or geo.get("conic", 0) != 0):
                raise ValueError("unsupported native surface geometry")
            if geo["type"] == "StandardGeometry" and finite(geo["radius"], "radius") == 0:
                raise ValueError("unsupported zero radius")
            if geo["type"] == "Plane" and geo["radius"] != math.inf:
                raise ValueError("unsupported invalid plane radius")
            cs = geo["cs"]
            if any(cs[k] != 0 for k in ("x", "y", "rx", "ry", "rz")) or cs.get("reference_cs"):
                raise ValueError("unsupported native decenter/tilt")
            if index:
                finite(cs["z"], "surface position")
                expected_z = (0 if index == 1 else
                              surfaces[index - 1]["geometry"]["cs"]["z"] + surfaces[index - 1]["thickness"])
                if not math.isclose(cs["z"], expected_z, rel_tol=1e-12, abs_tol=1e-10):
                    raise ValueError("unsupported inconsistent native positions and thicknesses")
                if finite(surface["thickness"], "thickness") < 0:
                    raise ValueError("unsupported negative native thickness")
            material = surface["material_post"]
            if material.get("propagation_model", {}).get("class") != "HomogeneousPropagation":
                raise ValueError("unsupported native material propagation")
            interaction = surface.get("interaction_model", {})
            if interaction.get("is_reflective") or interaction.get("coating") or interaction.get("bsdf"):
                raise ValueError("unsupported native reflection/coating/scattering")
        for surface in (surfaces[0], surfaces[-2], surfaces[-1]):
            material = surface["material_post"]
            if material.get("type") != "IdealMaterial" or material.get("index") != 1 or material.get("absorp") != 0:
                raise ValueError("unsupported non-air object/image space")
        if surfaces[-1]["geometry"]["type"] != "Plane":
            raise ValueError("unsupported curved image surface")
    except (KeyError, TypeError, IndexError) as error:
        raise ValueError("unsupported or malformed native Optiland prescription") from error


class OptilandBackend:
    """Own an isolated in-memory lens; never save over the initial source."""

    model_suffix = ".json"

    def __init__(self, modelpath):
        self.source = Path(modelpath).resolve()
        self.lens = None
        self._source_import = None
        self.import_restrictions = {"format": "Optiland native JSON", "restrictions": RESTRICTIONS}

    def __enter__(self):
        if version("optiland") != VERSION:
            raise ImportError(f"Optiland adapter requires optiland=={VERSION}")
        self.load(self.source)
        return self

    def __exit__(self, *_):
        self.lens = None

    def _open(self):
        if self.lens is None:
            raise RuntimeError("Optiland model is not open")
        return self.lens

    def load(self, path):
        from optiland.optic import Optic
        path = Path(path).resolve()
        if path.suffix.lower() == ".zmx":
            from optiland.fileio import load_zemax_file
            report = validate_zemax(path)
            # Resolve before the permissive reader runs: a near-spelling glass
            # must never become a substituted optical material.
            exact_glasses = [(definition, _exact_catalog_material(definition))
                             for definition in report["glass_definitions"]]
            lens = load_zemax_file(str(path))
            report["resolved_glasses"] = []
            for definition, exact in exact_glasses:
                surface = definition["surface"]
                indices = [{"wavelength_um": wave, "index": _material_index(exact, wave)}
                           for wave in report["wavelengths_um"]]
                matched = all(math.isclose(_material_index(lens.surfaces[surface].material_post,
                                                          item["wavelength_um"]), item["index"],
                                           rel_tol=1e-12, abs_tol=1e-12) for item in indices)
                # Persist exact lookup policy even when the converter found the
                # same glass; native reload must never return to fuzzy lookup.
                lens.updater.set_material(exact, surface)
                if any(not math.isclose(_material_index(lens.surfaces[surface].material_post,
                                                        item["wavelength_um"]), item["index"],
                                         rel_tol=1e-12, abs_tol=1e-12) for item in indices):
                    raise ValueError("exact catalog material assignment did not reproduce refractive indices")
                report["resolved_glasses"].append({**definition, "indices": indices,
                                                   "converter_indices_matched": matched,
                                                   "lookup_policy": "strict"})
            data = lens.to_dict()
        elif path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            _validate_native(data)
            _exact_native_catalogs(data)
            lens = Optic.from_dict(data)
            report = {"format": "Optiland native JSON", "restrictions": RESTRICTIONS}
        else:
            raise ValueError("unsupported model format; use native .json or restricted .zmx")
        _validate_native(data)
        self.lens = lens
        # Saved native snapshots keep the original ingestion provenance. Otherwise
        # restoring an imported baseline changes inspect() despite identical optics.
        if self._source_import is None:
            self._source_import = copy.deepcopy(report)
        self.import_restrictions = copy.deepcopy(self._source_import)

    def inspect(self):
        lens = self._open()
        data = _report_value(lens.to_dict())
        invariant = copy.deepcopy(data)
        surfaces = invariant["surface_group"]["surfaces"]
        del surfaces[-2]["thickness"]
        del surfaces[-1]["geometry"]["cs"]["z"]
        prescription = [{"index": i, "is_image": i == len(lens.surfaces) - 1,
                         "radius_mm": data["surface_group"]["surfaces"][i]["geometry"]["radius"],
                         "thickness_mm": data["surface_group"]["surfaces"][i].get("thickness")}
                        for i in range(len(lens.surfaces))]
        return {"engine": {"name": "Optiland", "version": VERSION},
                "focus_mm": float(lens.surfaces[-2].thickness), "invariants": invariant,
                "prescription": prescription, "surfaces": prescription,
                "axial_positions_mm": [s['geometry']['cs']['z'] for s in data['surface_group']['surfaces']],
                "image_surface": len(lens.surfaces) - 1,
                "import_restrictions": self.import_restrictions}

    def set_focus(self, mm):
        lens = self._open()
        mm = finite(mm, "focus_mm")
        if mm <= 0:
            raise ValueError("focus_mm must be positive")
        lens.updater.set_thickness(mm, len(lens.surfaces) - 2)

    def _surface(self, surface):
        lens = self._open()
        if type(surface) is not int or not 1 <= surface < len(lens.surfaces) - 1:
            raise ValueError("surface index must identify a physical surface, excluding object/image")
        return lens.surfaces[surface]

    def get_parameter(self, surface, name):
        selected = self._surface(surface)
        if name == "radius_mm":
            return float(selected.geometry.radius)
        if name == "thickness_mm":
            return float(selected.thickness)
        raise ValueError(f"unsupported parameter: {name}")

    def set_parameter(self, surface, name, value):
        self._surface(surface)
        value = finite(value, name)
        if name == "radius_mm" and value != 0:
            self.lens.updater.set_radius(value, surface)
        elif name == "thickness_mm" and value >= 0:
            if surface == len(self.lens.surfaces) - 2:
                self.set_focus(value)
            else:
                self.lens.updater.set_thickness(value, surface)
        else:
            raise ValueError(f"unsupported parameter or invalid value: {name}")

    def save(self, path):
        from optiland.fileio import save_optiland_file
        lens = self._open()
        path = Path(path).resolve()
        if path == self.source or (path.exists() and path.samefile(self.source)):
            raise ValueError("cannot overwrite source model")
        if path.suffix.lower() != ".json":
            raise ValueError("Optiland candidates must use native .json format")
        save_optiland_file(lens, str(path))

    def evaluate(self, spec):
        import numpy as np
        from optiland.analysis import SpotDiagram
        from optiland.mtf import FFTMTF
        lens = self._open()
        settings = spec.data["analysis"]
        requested = {metric_key(row): row for row in spec.data["requirements"]}
        for objective in spec.objective_metrics:
            requested.setdefault(metric_key(objective), objective)
        rows, mtf_cache = [], {}
        for req in requested.values():
            name = req["metric"]
            row = {k: req[k] for k in ("metric", "field", "wavelength", "frequency", "axis") if k in req}
            row.update(value=None, unit=UNITS[name], analysis=copy.deepcopy(settings))
            rows.append(row)
            try:
                if name in {"efl_mm", "f_number"}:
                    row["analysis"].update(wavelength=lens.wavelengths.primary_index + 1,
                                           wavelength_um=float(lens.primary_wavelength))
                if name == "efl_mm":
                    value = lens.paraxial.f2()
                elif name == "f_number":
                    value = lens.paraxial.FNO()
                elif name == "total_track_mm":
                    value = lens.surfaces[-1].geometry.cs.z - lens.surfaces[1].geometry.cs.z
                elif name == "image_distance_mm":
                    value = lens.surfaces[-2].thickness
                else:
                    if settings["use_polarization"]:
                        raise ValueError("polarization analysis unsupported by this adapter")
                    fi, wi = req["field"] - 1, req["wavelength"] - 1
                    if not 0 <= fi < len(lens.fields) or not 0 <= wi < len(lens.wavelengths):
                        raise ValueError("field/wavelength index unavailable in model")
                    field = lens.fields[fi]
                    maxfield = float(lens.fields.max_field)
                    coord = (0.0, float(field.y) / maxfield if maxfield else 0.0)
                    wavelength = float(lens.wavelengths[wi].value)
                    row["analysis"].update(field_xy_deg=[float(field.x), float(field.y)],
                                           wavelength_um=wavelength, scalar=True)
                    if name == "rms_spot_um":
                        rings = max(4, settings["sampling"] // 4)
                        spot = SpotDiagram(lens, fields=[coord], wavelengths=[wavelength],
                                           num_rings=rings, reference="centroid")
                        expected_rays = 1 + 3 * rings * (rings + 1)
                        transmitted_rays = len(spot.data[0][0].x)
                        row["analysis"].update(sampled_rays=expected_rays, transmitted_rays=transmitted_rays)
                        if transmitted_rays != expected_rays:
                            raise ValueError("sampled rays were lost or vignetted; RMS cannot certify full-pupil performance")
                        value = float(spot.rms_spot_radius()[0][0]) * 1000
                        row["analysis"].update(method="geometric RMS radius about centroid",
                                               distribution="hexapolar", num_rings=rings)
                    elif name == "mtf":
                        if (fi, wi) not in mtf_cache:
                            mtf_cache[fi, wi] = FFTMTF(lens, fields=[coord], wavelength=wavelength,
                                                      num_rays=settings["sampling"])
                        mtf = mtf_cache[fi, wi]
                        tangential = req["axis"] == "tangential"
                        frequencies = np.asarray((mtf.freq_tang if tangential else mtf.freq_sag)[0])
                        values = np.asarray(mtf.mtf[0][0 if tangential else 1])
                        if (not np.all(np.isfinite(frequencies)) or not np.all(np.isfinite(values))
                                or not np.all(np.diff(frequencies) > 0)
                                or not frequencies[0] <= req["frequency"] <= frequencies[-1]):
                            raise ValueError("requested frequency outside valid computed MTF grid")
                        value = np.interp(req["frequency"], frequencies, values)
                        row["analysis"].update(method="scalar FFT MTF", interpolation="linear, no extrapolation",
                                               frequency_range_cyc_per_mm=[float(frequencies[0]), float(frequencies[-1])])
                    else:
                        raise ValueError("metric unsupported by Optiland adapter")
                row["value"] = finite(float(value), name)
            except (ValueError, IndexError, RuntimeError, ArithmeticError) as error:
                row["reason"] = str(error)
        return rows
