# Your first optical workflow

[Documentation](README.md) / Quickstart

Run a calculator, refocus a synthetic singlet, and generate a review you can open
in a browser. **No OpticStudio license is needed.**

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.
uv can provision the requested Python and dependencies on first use; allow time for
those downloads. The command examples below work in PowerShell and common Unix shells.

## Open the example directory

If you [installed the skill](install.md), open a terminal in its `optical-design`
directory, the one containing `SKILL.md`, `scripts/`, and `assets/`.

Alternatively, use a standalone checkout in a new directory:

```sh
git clone --branch v1.1.0 --depth 1 https://github.com/tangericm/optical-design.git
cd optical-design/skills/optical-design
```

Run the rest of this guide from that skill directory.

## Calculate the diffraction limit

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

## Refocus a lens

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

## Open the review

```sh
uv run scripts/review.py --report quickstart-focus/report.json --out quickstart-review --json
```

Open `quickstart-review/report.html` in your browser. The folder must be new.
The review collects the recorded outcome, metric comparisons, prescription changes,
and evidence into one readable page.

| Keep this file | What it contains |
|---|---|
| `quickstart-focus/candidate-model.json` | The saved candidate lens |
| `quickstart-focus/report.json` | The job's machine-readable evidence and acceptance checks |
| `quickstart-review/report.html` | The standalone visual review |
| `quickstart-review/report.md` | A Markdown version for reading or sharing |
| `quickstart-review/manifest.json` | Hashes and verification details for the review |

Review rendering can also succeed for a failed optical job. Read the recorded outcome;
rendering success is not a separate optical acceptance test. Keep the original job
folder and its artifacts together if you need to regenerate the review.

## Continue with your own requirements

Use the [model contract and specification guide](../skills/optical-design/references/design-workflow.md)
before substituting your own lens. Example requirements belong to the synthetic
singlet; they are not defaults for an unrelated system.

Next, [inspect and edit a model](../skills/optical-design/references/model-actions.md),
[optimize multiple variables](../skills/optical-design/references/optimization.md), or
[run the complete workflow example](../skills/optical-design/evals/README.md).
