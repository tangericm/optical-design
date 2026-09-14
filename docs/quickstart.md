# Quickstart

[Documentation](README.md) / Quickstart

Run a calculator, refocus a synthetic singlet, and generate a review you can open in a
browser. No OpticStudio license is needed.

## One command

Install [Node.js](https://nodejs.org/en/download) 22+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/), then open a terminal in
your project folder:

```sh
npx optical-design doctor
npx optical-design demo --out my-first-lens
```

Use a new output directory. The first run may download Python and Optiland. The demo
calculates a diffraction limit, adjusts the example lens's final air gap, verifies the
saved candidate, and creates an HTML review. Open the review path printed at completion;
the source model stays unchanged.

| Output | What to look for |
|---|---|
| Job outcome | Whether the candidate improved and met the stated requirements |
| Prescription changes | The original and final spacing, with the remaining lens geometry fixed |
| Analysis settings | Fields, wavelengths, sampling, metric definitions, and units |
| Saved-model checks | Whether the saved and reloaded candidate matches the reported result |
| Review package | A readable view of the recorded evidence; it can also describe a failed job |

The requirements are specific to the synthetic model, and an HTML report is not by
itself proof that a design passed. Prefer individual commands? Continue below.

## Step by step

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.
uv can provision the requested Python and dependencies on first use; allow time for
those downloads. The command examples below work in PowerShell and common Unix shells.

Open the example directory. If you [installed the skill](install.md), open a terminal
in its `optical-design` directory, the one containing `SKILL.md`, `scripts/`, and
`assets/`. Alternatively, use a standalone checkout:

```sh
git clone --branch v1.1.0 --depth 1 https://github.com/tangericm/optical-design.git
cd optical-design/skills/optical-design
```

Run the rest of this guide from that skill directory.

### Calculate the diffraction limit

```sh
uv run scripts/resolve.py airy --wavelength-um 0.55 --fnum 4 --json
```

The JSON result includes:

| Quantity | Expected value |
|---|---|
| Airy first-zero radius | 2.684 µm |
| Airy first-zero diameter | 5.368 µm |

This is a scalar, clear circular pupil calculation in image-space air at 550 nm and
f/4. The diameter is twice the radius; neither quantity is the FWHM.

### Refocus a lens

The included singlet is deliberately defocused. This command searches only the final
air gap within the bundled specification's bounds:

```sh
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py refocus --backend optiland --model assets/portable-singlet.json --spec assets/refocus-spec.json --out quickstart-focus --json
```

Use a new or empty `quickstart-focus` folder. On a repeat run, choose another name.
The source model in `assets/` stays unchanged.

Open `quickstart-focus/report.json`. For this example, expect `status: "improved"`
and `saved_candidate_verified: true`. Check the requirements before using the saved
candidate. A candidate file's existence alone does not establish success.

### Open the review

```sh
uv run scripts/review.py --report quickstart-focus/report.json --out quickstart-review --json
```

Open `quickstart-review/report.html` in your browser. The folder must be new. The
review collects the recorded outcome, metric comparisons, prescription changes, and
evidence into one readable page.

| Keep this file | What it contains |
|---|---|
| `quickstart-focus/candidate-model.json` | The saved candidate lens |
| `quickstart-focus/report.json` | The job's machine-readable evidence and acceptance checks |
| `quickstart-review/report.html` | The standalone visual review |
| `quickstart-review/report.md` | A Markdown version for reading or sharing |
| `quickstart-review/manifest.json` | Hashes and verification details for the review |

Review rendering can also succeed for a failed optical job. Read the recorded outcome;
rendering success is not a separate optical acceptance test.

## Your own lens

Point your agent at your `.zmx`, `.zos` or Optiland JSON file and let it write the
Optiland code directly, following [SKILL.md](../skills/optical-design/SKILL.md) and the
[Optiland recipes](../skills/optical-design/references/optiland-recipes.md):

1. **Inspect it.** `uv run --python 3.11 --with optiland==0.6.2 scripts/inspect_zmx.py --model your-lens.zmx --json` reports the surface table, fields, wavelengths, and which Zemax directives Optiland ignored as cosmetic.
2. **Run the first-order gate.** `uv run --python 3.11 --with optiland==0.6.2 scripts/first_order.py --model your-lens.zmx --json` reports EFL, F-number, total track, chromatic focal shift, and telecentricity error — check these against your spec before anything else, since EFL, magnification and track length are coupled.
3. **Look, then diagnose.** Recipe 3 (layout) and recipe 4 (spot diagram) show the geometry and blur; recipe 7 (Seidel and third-order) names which aberration dominates. See [diagnosis.md](../skills/optical-design/references/diagnosis.md) for how to turn the Seidel table and fans into a two-sentence verdict.
4. **Optimize.** Recipe 9 (`OptimizationProblem` with `LeastSquares`) is the standard damped-least-squares path: first-order operands first, then RMS spot at 0/0.5/0.8/0.9 of full field, then wavefront or MTF. Recipe 10 adds a global search when the local optimizer gets stuck; recipe 11 substitutes glass with `GlassExpert`.
5. **Render a review.** `uv run scripts/render_review.py --summary summary.json --out review --json` turns a `summary.json` (model, hashes, first-order numbers, metrics, figure paths, verdict) plus the PNGs from the recipes above into one self-contained HTML page. `render_review.py --help` documents the input contract in full.

Starting a new design instead of editing one? Pick a form from the
[forms library](../skills/optical-design/assets/forms/README.md) by F-number, field and
NA, and scale it to your EFL.

### Audited mode

For a hash-verified receipt on a bounded change — restricted to spherical/plane
prescriptions, radius/thickness variables only, and a handful of scalar metrics —
`scripts/design.py` is a narrower, older path still available for teams that need that
discipline enforced by a job runner rather than by an agent following SKILL.md:

```sh
uv run --python 3.11 --with optiland==0.6.2 scripts/design.py refocus --backend optiland --model assets/portable-singlet.json --spec assets/refocus-spec.json --out quickstart-focus --json
```

This is the same command as the refocus step above. See
[audited mode](../skills/optical-design/references/audited/README.md) for its full
scope, commands, and acceptance rules.

## Continue

To hand the tool your own saved prescription, ask your agent:

> Use optical-design to inspect [model path]. Check that its surface types and analysis
> assumptions are supported. Summarize the current design, name the dominant
> aberration, and preserve the source model.

Next: [command reference](install.md#command-reference), [capabilities and limits](capabilities.md),
or [run the complete workflow example](../skills/optical-design/evals/README.md).
