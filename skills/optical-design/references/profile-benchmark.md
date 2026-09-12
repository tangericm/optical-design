# Native intensity-profile benchmarks

Use `scripts/benchmark.py` to reproduce Huygens or physical optics propagation (POP)
profiles on unchanged sequential models. This workflow verifies a numerical reference;
it does not optimize a prescription or decide whether the physical design meets a requirement.

## Invocation and ownership

From the repository root, use a licensed Windows OpticStudio installation and pinned dependencies:

```powershell
uv run --python 3.11 --with zospy==2.1.5 --with pythonnet==3.1.0 skills/optical-design/scripts/benchmark.py --manifest docs/research/real-benchmark/manifest.json --out benchmark-run --json
```

Use a new or empty output directory. The runner verifies declared input hashes, copies each
model and owns a standalone native session. It does not attach to the user's editor or save
prescription changes to the original. Analysis settings, including POP resampling, can change
inside the disposable session. Model copies are restored between cases. Keep the engine,
catalog/coating provenance, settings readback, warnings and original coordinate arrays with
the numerical result. A hash or analysis failure is not a successful reference check.

Without a `reference` entry, a successful run has `status: "completed"` and
`reference_validated: false`. Inspect both fields; completion alone does not mean reference
agreement. With a reference, compare the complete model/case/axis set using the declared
tolerances. Even exact agreement is same-method reproduction, not independent physical validation.

## Manifest

The strict schema requires `schema_version`, `name`, `models` and `cases`. Optional
`reference` and `comparison` must be supplied together or both omitted. Do not insert
provenance annotations as undeclared keys. Every model runs
every shared case: three models and 25 cases produce 75 model/case records.

This minimal example requires replacement paths and actual SHA-256 hashes:

```json
{
  "schema_version": 1,
  "name": "Saved planar X reference",
  "models": [
    {"id": "Stock", "path": "C:/models/SamplePath_Stock.ZMX", "sha256": "REPLACE_WITH_MODEL_SHA256"}
  ],
  "cases": [
    {
      "id": "huygens_x_w0_p512_i128",
      "method": "huygens",
      "field": 1,
      "wavelength": 0,
      "polarization": true,
      "axis": "x",
      "pupil": 512,
      "image": 128,
      "delta_um": 6,
      "reference": "Planar"
    }
  ],
  "reference": {"path": "reference.json", "sha256": "REPLACE_WITH_REFERENCE_SHA256"},
  "comparison": {"rtol": 1e-6, "atol": 1e-8, "coordinate_atol_mm": 1e-10}
}
```

Model paths may be absolute; relative paths resolve against the manifest. The reference path
also resolves against the manifest. IDs must be unique ignoring case within their model/case lists and use
letters, digits, `_` or `-`. `comparison` requires finite nonnegative `rtol` and `atol`;
`coordinate_atol_mm` is optional and defaults to `1e-10` mm. Coordinate tolerance is separate
from intensity/power tolerance. Matching scalar widths cannot substitute for matching arrays,
grid coordinates and identities. These example tolerances concern numerical reproduction,
not a claim of submicron optical accuracy.

Case fields are exact and method-specific; unknown or missing keys fail validation:

| Setting | Huygens | POP |
|---|---|---|
| `method` | `huygens` | `pop` |
| `field` | Positive native 1-based index | Positive native 1-based index |
| `wavelength` | 0 for all active wavelengths, otherwise native 1-based index | Positive native 1-based index; separate case per wavelength |
| `polarization` | Explicit boolean | Explicit boolean |
| Sampling | `pupil`, `image`: 32, 64, 128, 256, 512 or 1024 | `sampling`: 128, 256, 512, 1024, 2048 or 4096 |
| Other required fields | `axis`: x/y; positive `delta_um`; `reference`: Planar/Spherical | Positive `window_mm`, `waist_x_mm`, `waist_y_mm`, `power_w`; `start_surface`, `end_surface`; boolean `separate_xy`; `resampling` list |

A complete POP case for a 840 nm Gaussian source might be:

```json
{
  "id": "pop_w9_n1024",
  "method": "pop",
  "field": 1,
  "wavelength": 9,
  "polarization": true,
  "sampling": 1024,
  "window_mm": 0.4,
  "waist_x_mm": 0.002471428571428571,
  "waist_y_mm": 0.002471428571428571,
  "start_surface": 1,
  "end_surface": 28,
  "power_w": 1,
  "separate_xy": true,
  "resampling": [
    {"surface": 4, "width_mm": 8},
    {"surface": 15, "width_mm": 64},
    {"surface": 24, "width_mm": 64}
  ]
}
```

These source and resampling numbers are an example prescription's analysis recipe, not defaults
for another lens. POP uses GaussianWaist, zero surface-to-beam distance, explicit X/Y waist
radii and launched power; unused beam parameters are zero. The listed resampling planes
declare the complete enabled schedule within the propagated surface range. The initial
computational window is not the final-plane extent or a mechanical clear aperture.

The reference file has a single `records` array. Each record has `model_id`, `case_id`,
`profiles`, and optional integrated `power_w`. Each axis profile contains `x_mm` and
`intensity` numerical arrays of equal length. Huygens contributes the requested single axis;
POP contributes both `x` and `y`. Despite the shared key `x_mm`, the coordinates are along
the named profile axis. Require exactly one record per model/case and the correct axes.

## Coordinate and intensity contract

- Native Huygens cross-section coordinates and `ImageDelta` are in **µm** for these mm
  models. The adapter verifies spacing and converts coordinates to `x_mm` by dividing by
  1000. It explicitly requests central RowCol=0, linear X/Y, Normalize=true and
  UseCentroid=false. The returned profile is a normalized intensity cut, not absolute power.
- POP retains absolute irradiance in W/mm². For saved legacy evidence, raw `x`/`y` keys
  contain irradiance arrays. Coordinates are **`MinX + i*Dx` / `MinY + j*Dy` in mm**.
  The benchmark deliberately preserves this native index convention; do not silently add
  a half-pixel offset, recenter the peak or replace it with another wrapper's grid convention.
  The X cut takes the row nearest Y=0, and Y the column nearest X=0. Retain their actual
  orthogonal coordinates and native pitch. Historical zero-index selection used
  `Math.Round(-Min/step)`; exact half-cell ties need explicit checking when importing another dataset.
- POP `power_w` is full-grid irradiance sum times Dx·Dy. A one-dimensional cut integral
  is not transmitted power. A central cut is also not a marginal integrated over the other
  coordinate. Illumination-line cuts do not become local point-image PSFs because the
  native analysis name contains “PSF”. Define source, observation plane and quantity.

For an incoherent spectral mean, normalize the intended active spectral weights, multiply
each **absolute** monochromatic irradiance by its weight and sum before any peak scaling.
The reusable spectral combiner applies supplied weights as-is; it does not normalize them
implicitly. Declare whether weights mean a mean or an absolute power distribution.
Do not sum independently peak-normalized monochromatic profiles, sum coherent field
amplitudes as intensities, or include inactive serialized wavelengths. Huygens wavelength 0
uses the native active spectrum; it is not a sum of the saved monochromatic convergence cases.

## Sampling and interpretation

Widths are full outermost crossings of sampled-peak intensity at 0.5 and exp(−2), with linear
interpolation only between adjacent samples. They are not Gaussian-fit widths, second moments,
connected-lobe widths or an optical acceptance criterion. Missing outer crossings make a width
unavailable; too few samples in a threshold component mark it undersampled even when an
interpolated number exists. Multiple connected segments are reported rather than hidden.

Flatness CV uses population standard deviation divided by mean of original samples in the
fixed ROI, without peak recentering. The entire ROI must be covered, with at least five samples
and no gap greater than one quarter of its width. Inspect `cv_roi_status`, `roi.fully_covered`,
native grid pitch, edge warnings and threshold status. A narrow Y window cannot establish X's
0.42 mm flatness requirement; a partial ROI is not silently accepted.

Spectral interpolation aligns differing native grids on their common overlap; it adds no
spatial information and is not energy-conserving rebinning. Preserve each source grid's pitch
and provenance rather than claiming the dense union/reporting grid as native resolution.
Sampling diagnostics are minimum checks, not convergence certificates. Refine pupil sampling,
image/propagation sampling and window independently when a conclusion depends on them.
Matching curves from one saved recipe cannot resolve a Huygens–POP disagreement.

If contributing cuts declare `orthogonal_position_mm`, all must declare it and agree within
1e-12 mm absolute numerical roundoff. The combiner preserves those positions and rejects
misaligned cuts; it does not interpolate perpendicular to the cut. Zero-weight rows do not
set the identity of the sum.

## Supported scope and research evidence

The native profile backend permits complex surface prescriptions and native polarization
settings in mm, single-configuration sequential models. This broader analysis path does not
expand the centered spherical/plane, scalar prescription audit/refocus/tolerance adapters.
It does not certify arbitrary surface data, beam launch, polarization/coating assumptions or
catalog accuracy. POP supports the explicit Gaussian-waist launch above, not arbitrary measured
or imported fields. Non-sequential paths, source calibration, OCT SNR and manufacturing
acceptance require separate evidence.

The repository's `docs/research/real-benchmark/reference-audit.md` records the OCT example's
exact model/raw-file hashes, 18-wave spectrum, boundaries, baseline widths and uncertainty.
`manifest.json` and `reference.json` in that repository directory contain 25 shared cases over
three models (75 records). Consult that research evidence for this particular benchmark;
the shipped skill does not require access to the original external project. Saved references
and a validated manifest alone do not establish a fresh native pass.
