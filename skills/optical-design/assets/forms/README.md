# Starting-point forms library

Eleven starting designs for lens-design problems, each shipped as `.zmx` (Zemax-format,
written by `optiland.fileio.save_zemax_file`) and Optiland JSON
(`save_optiland_file`), plus a `<name>.md` commentary. Load whichever format your
backend prefers; both describe the same prescription and were cross-checked against
each other (see Verification below).

Seven of the eleven come straight from `optiland.samples` (Cooke triplet, Tessar,
Double Gauss, Petzval, telephoto, and the 20x/60x microscope objectives) — real,
well-known forms already curated in Optiland. The other four (both achromats, the OCT
scan lens, the 4f relay) are built here from catalog glass and a short damped
least-squares polish (`optiland.optimization.LeastSquares`), because Optiland ships no
sample for them. Only the achromats are corrected to a clean starting point; the OCT
scan lens and the 4f relay are deliberately left with real residuals for the
learning exercises to explore. These forms are not validated manufacturing designs.

Only Erfle is available under `optiland.samples.eyepieces` (no Plössl), so a Plössl
eyepiece form was not added — see "What didn't make it" below.

## Index

Half field is the full field half-angle for imaging forms, entrance-pupil NA for the
infinity-corrected microscope objectives (see their commentary — they are modeled in
the reverse-trace convention Optiland's samples use, tube-lens side first), and scan
half-angle for the OCT lens. On-axis RMS spot is the geometric spot radius at the
primary wavelength, `Hx=Hy=0`, hexapolar sampling. Elements counts pieces of glass, so
a cemented doublet counts 2.

| Form | EFL (mm) | F/# | Half field / NA | Wavelengths (nm) | Elements | On-axis RMS (µm) |
|---|---|---|---|---|---|---|
| [cemented-achromat-doublet](cemented-achromat-doublet.md) | 50.00 | 5.00 | 5.0 deg | 486.1, 587.6, 656.3 | 2 | 5.3 |
| [air-spaced-achromat](air-spaced-achromat.md) | 100.00 | 4.00 | 4.0 deg | 486.1, 587.6, 656.3 | 2 | 3.8 |
| [cooke-triplet](cooke-triplet.md) | 50.00 | 5.00 | 20.0 deg | 480.0, 550.0, 650.0 | 3 | 4.3 |
| [tessar](tessar.md) | 4.00 | 4.50 | 20.5 deg | 486.1, 587.6, 656.3 | 4 | 0.5 |
| [double-gauss](double-gauss.md) | 100.00 | 5.00 | 14.0 deg | 486.1, 587.6, 656.3 | 6 | 11.2 |
| [petzval](petzval.md) | 50.58 | 1.40 | 7.0 deg | 486.1, 587.6, 656.3 | 4 | 96.7 |
| [telephoto](telephoto.md) | 127.02 | 5.60 | 10.0 deg | 486.1, 587.6, 656.3 | 5 | 10.9 |
| [microscope-objective-20x](microscope-objective-20x.md) | 7.86 | 0.97 | NA 0.52 | 486.1, 587.6, 656.3 | 6 | 48.9 |
| [microscope-objective-60x](microscope-objective-60x.md) | 98.58 | 0.90 | NA 0.56 | 486.1, 587.6, 656.3 | 9 | 11.5 |
| [oct-semi-plossl-scan-lens](oct-semi-plossl-scan-lens.md) | 36.00 | 9.00 | +/-6.0 deg scan | 800.0, 840.0, 900.0 | 4 | 102.4 (unbalanced) |
| [4f-relay-tube-lens](4f-relay-tube-lens.md) | afocal | F/50 per element | +/-1.0 deg | 486.1, 587.6, 656.3 | 4 | n/a (collimated) |

EPD, image distance (historically labeled `bfl`) and total track for every form are in `_build_summary.json` in
this directory (build provenance, not part of the shipped form set) alongside the raw
reload-verification numbers.

## Learning status and provenance

| Forms | Use as | Important condition |
|---|---|---|
| Cemented and air-spaced achromats | Educational imaging starts | Verify focus and the required field/wavelength envelope |
| Cooke triplet, Tessar, double Gauss, Petzval, telephoto | Reference design forms | A familiar form does not imply corrected performance for a new specification |
| Microscope objectives 20x/60x | Reverse-trace structure references | Names come from upstream samples; establish manufacturer, magnification convention and real NA separately |
| OCT semi-Plössl | Deliberately unbalanced exercise | Large nominal blur; intended for rebalancing, not direct use |
| 4f relay | Afocal pupil-relay example | Judge collimation and pupil matching, not spot at the arbitrary observation plane |

Seven forms are adapted from [Optiland 0.6.2 samples](https://github.com/optiland/optiland/tree/v0.6.2/optiland/samples).
Optiland is copyright 2024 Kramer Harrison under the MIT license; its notice is retained
in the [skill license](../../LICENSE). The other four forms were constructed for this
project. Attribution is not a claim of validation for a particular product. The saved
build summary records historical measurements; its `bfl` values denote the original
final air gap, not independently computed back focal length.

## Picking a start from a specification

- Need a fast, cheap, narrow-field relay (finder scope, laser collimation, a single
  achromatic doublet for an OCT or beam-relay design) — start from
  **cemented-achromat-doublet** or **air-spaced-achromat** depending on how much
  spherochromatism budget you have (air-spaced buys another surface's worth of
  correction for a small assembly cost).
- Need a compact general-purpose lens at f/4-f/6 with 30-40 degrees full field —
  **cooke-triplet** (three variables, easy to understand) or **tessar** (adds a
  cemented pair for one more degree of freedom) beat a doublet badly past about 10
  degrees half field.
- Need a fast normal lens (f/1.4-f/2) with a flat, well-corrected field to 20-28
  degrees full field — **double-gauss**.
- Need speed above field (f/1.4-f/2, narrow field, projection or a fast relay) —
  **petzval**, and budget a field flattener or accept curvature.
- Need a long-focus, physically short package — **telephoto**.
- Studying a reverse-traced microscope objective and its tube-lens convention —
  **microscope-objective-20x** or **microscope-objective-60x**, read alongside
  `references/microscopy.md` for the tube-lens convention math.
- Building an OCT sample arm or a galvo-scanned imaging path — **oct-semi-plossl-scan-lens**,
  and expect to rebalance it (that is eval scenario 3).
- Relaying a pupil or an intermediate image in infinity space (between two
  infinity-corrected microscope stages, or around a scanner/SLM) —
  **4f-relay-tube-lens**.

## Verification

Every `.zmx` was written from the Optiland `Optic` object also saved as JSON, then
reloaded with `optiland.fileio.load_zemax_file` and re-measured. Paraxial EFL and F/#
of the reloaded `.zmx` agreed with the saved JSON model to better than `2e-4` percent
(relative) for all eleven forms — three to four orders of magnitude inside the 0.1
percent bar. Commands used, from `skills/optical-design/`:

```bash
uv run --python 3.11 --with optiland==0.6.2 --with matplotlib python - <<'PY'
from optiland.fileio import load_zemax_file, load_optiland_file
z = load_zemax_file("assets/forms/cemented-achromat-doublet.zmx")
j = load_optiland_file("assets/forms/cemented-achromat-doublet.json")
print(z.paraxial.f2(), j.paraxial.f2())
print(z.paraxial.FNO(), j.paraxial.FNO())
PY
```

or, for a printed report using the first-order extractor:

```bash
uv run --python 3.11 --with optiland==0.6.2 scripts/first_order.py --model assets/forms/cemented-achromat-doublet.zmx --json
```

## What didn't make it

- **Plössl eyepiece.** `optiland.samples.eyepieces` ships only `EyepieceErfle`; there is
  no Plössl sample to draw on, and hand-deriving one accurately from thin-lens theory
  under the same verification bar as the rest of this set was out of scope for this
  pass. Eleven forms ship instead of twelve.
- **oct-semi-plossl-scan-lens is not yet a good lens.** It hits its EFL, pupil and
  telecentricity targets exactly, but on-axis RMS spot is 102 µm against an 840 nm f/9
  Airy radius of about 9 µm — spherochromatism from the two 90-degree-orientation
  cemented interfaces dominates. That gap is the point: eval scenario 3 asks an agent
  to rebalance exactly this file. See its commentary for what to vary first.
- **4f-relay-tube-lens has no meaningful on-axis spot number.** It is afocal by
  construction (paraxial EFL run into the millions of mm — read that as "infinite," not
  as a real focal length); the "image" surface is a 50 mm observation plane past the
  second lens where a collimated beam is still 4 mm wide, not a focus. Judge it on
  marginal- and chief-ray collimation instead (see its commentary).
