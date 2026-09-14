# Capabilities and limits

[Documentation](README.md) / Capabilities

This page describes the unreleased source checkout; see [compatibility](compatibility.md)
for published-version scope and [quickstart](quickstart.md) for executable preview commands.

## Choose a workflow

| Task | Implementation | What it establishes |
|---|---|---|
| Learn with a lens | `npx optical-design walkthrough --out NEW-DIRECTORY` | Controlled focus change, before/after figures and saved-candidate measurements |
| Calculate a limit | `resolve.py`: resolution, depth of focus, Gaussian beams, OCT, camera sampling | Closed-form results under stated scalar/paraxial assumptions |
| Interpret wavefront data | `zernike.py`, `wavefront.py`, `interfero.py` | Scalar wavefront/PSF/MTF or interferogram quantities with conventions and sampling |
| Inspect a prescription | `inspect_zmx.py` and `first_order.py` | Import-fidelity assessment, first-order quantities and optional gates |
| Design or improve a lens | Fourteen Optiland recipes and eleven starting forms | Agent-written analysis, optimization and tolerance code; final requirements checked separately |
| Share a review | `render_review.py` | Self-contained HTML from a versioned summary and PNGs; rendering verifies no optics |
| Make a bounded audited change | `design.py`, `review.py`, optional local job server | Copy/hash, hard requirements, saved-candidate reload and bounded mutation evidence; HTML/Markdown reviews |

## File formats and engines

| Input or feature | Portable path | Licensed native path |
|---|---|---|
| Zemax `.zmx` | Optiland reader plus import assessment; unsupported content remains visible | Audited adapter within its sequential subset |
| Optiland `.json` | Optiland native format | Not a native OpticStudio input |
| OpticStudio `.zos` | Unsupported; export a supported `.zmx` in OpticStudio or use native mode | Windows and valid OpticStudio API license |
| Layout, spot, fans, Seidel, wavefront/MTF | Tested Optiland 0.6.2 recipe examples | Separate ZOSPy/API code needed; no drop-in recipe equivalence |
| Audited edits, refocus, optimization, sensitivity, tolerances | Spherical/plane systems; radius/thickness variables | Fixed Standard conics and EvenAspheric A2–A16 also supported |
| Huygens/POP benchmark | Unavailable | Same-method profile reproduction on unchanged models |

Use Python 3.11+ and uv. Portable commands use `uv run --python 3.11 --with optiland==0.6.2`.
Native commands use ZOSPy 2.1.5 and pythonnet 3.1.0; Python 3.11 is the recorded native
runtime. Installation success, engine readiness, native licensing and end-to-end agent
host behavior are separate checks. See [compatibility](compatibility.md).

## Measurement and acceptance

Back focal length is measured from the last optical vertex to paraxial focus. Image
distance locates the actual image plane and may differ. The `bfl_mm` key remains an
alias for corrected back focal length; use `image_distance_mm` for detector spacing.
First-order NA and chief-ray angle are paraxial quantities, distinct from real-ray or
high-NA measurements. EFL spread over wavelength is not a best-focus search.

Inspection preserves import warnings through analysis. Non-mm data needs conversion
before a mm-based gate can accept it. A directive ignored by a reader is not automatically
cosmetic. Optiland's native capabilities do not imply every imported Zemax surface or
setting is represented faithfully.

Optimizer bounds on operands may be penalties. Re-measure hard requirements independently
on the saved candidate at declared fields, including the required edge, wavelengths and
sampling. Reports distinguish supplied interpretation, measured results and recorded
reload evidence. A failed design can still have a useful review.

## Scope

The audited adapter remains narrower than direct Optiland programming: at most four
radius/thickness optimization variables, centered sequential geometry, mm units, fixed
solves and its documented scalar metrics. Coatings, coordinate breaks, explicit apertures
and multiple configurations are outside its acceptance contract. Consult the
[audited reference](../skills/optical-design/references/audited/README.md).

Supported workflows do not cover non-sequential/stray-light design, thin-film design,
illumination/non-imaging optics or manufacturing release. High-NA and polarization-sensitive
work needs an appropriate vector model. See
[evidence limits](../skills/optical-design/references/evidence-limits.md).

## Evaluation

[Repository evaluations](https://github.com/tangericm/optical-design/tree/main/evals)
contain fixed-budget tasks, grading guidance and historical results. They are excluded
from installed skills and npm artifacts. Historical five-pair results are preliminary;
passing regression tests implies no new cross-model speed or correctness guarantee.
