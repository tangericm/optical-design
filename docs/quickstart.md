# Your first lens

[Documentation](README.md) / Quickstart

Start with a picture and one measured improvement. You do not need a lens file,
OpticStudio license, or knowledge of Python to run the walkthrough.

## Run the guided example

Install [Node.js](https://nodejs.org/en/download) 22+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/), then open a terminal
in your project directory:

```sh
npx optical-design@latest doctor
npx optical-design@latest walkthrough --out my-first-lens
```

Use a new output directory. The first run may download Python 3.11 and Optiland 0.6.2;
subsequent runs reuse the dependency cache. To explicitly check the portable engine,
run `npx optical-design@latest doctor --engine-check`; this may also download dependencies.
A default doctor check does not run the engine or verify native licensing.

The walkthrough copies a bundled Cooke triplet, introduces a known focus offset,
searches a bounded image distance, and saves and reloads the candidate. Open the
HTML review path printed at completion. Results belong to your project; the
installed skill stays unchanged.

Look for four things:

1. **Layout:** the lens bends rays toward the image. The detector position matters.
2. **Before and after:** the spot shows where rays from one object point arrive.
   A smaller geometric RMS radius means a tighter distribution under that sampling.
3. **Requirements:** inspect each field and wavelength. A lower combined merit does
   not mean every field improved or every target passed.
4. **Saved candidate:** reload measurements check the delivered file. They do not
   prove manufacturing yield or a global optimum.

This is a controlled focus exercise, not a manufacturing-ready triplet.
Cold-download time depends on your connection. Watch the stage messages; a
budget limit or failed target should be part of the result.

On the development Windows machine, the warmed optical work took about 10 seconds
and worst sampled RMS radius improved from **85.03 to 18.76 µm** across the nine
field/wavelength pairs. This is a measured example, not a setup-time guarantee;
dependency downloads and process startup add time.

## Use it with your agent

[Install the skill](install.md), start a new conversation, and choose a task:

> Use optical-design to run its bundled walkthrough. Explain the pictures without
> assuming I know optical design, and save the results in my project.

> Will my camera pixels sample my microscope adequately? Help me find the objective
> NA, total magnification and wavelength needed, then calculate the answer.

> Inspect my attached lens with optical-design. Check units and import fidelity,
> then explain the main limitation and a small useful change against my requirements.

The agent resolves scripts and assets from the installed `SKILL.md`. Keep all
generated scripts, candidate lenses and figures in one project output directory
outside the installation.

## A calculator without an optical engine

An agent invokes `scripts/resolve.py` using its absolute installed path:

```text
uv run --python 3.11 <absolute-skill-directory>/scripts/resolve.py airy --wavelength-um 0.55 --fnum 4 --json
```

Replace the placeholder with the directory containing `SKILL.md`; quote paths
containing spaces. At 550 nm and f/4, the scalar clear-circular-pupil Airy
first-zero radius is **2.684 µm**, and its diameter is **5.368 µm**. Neither is FWHM.

## Your own prescription

| Input | First action | Needs |
|---|---|---|
| `.zmx` | Import-fidelity assessment, then first-order analysis | Optiland 0.6.2; correctly interpreted units |
| Optiland `.json` | First-order analysis and selected diagnostics | Optiland 0.6.2, compatible model serialization |
| `.zos` | Native audited inspection through `design.py` | Windows, OpticStudio and valid API license |

The agent adapts the relevant [recipe](../skills/optical-design/references/optiland-recipes.md),
preserves the source, and checks hard requirements on the saved, reloaded candidate.
Parsing a file does not establish faithful conversion. Unsupported import content
remains visible in the analysis and review.

The [native reference](../skills/optical-design/references/opticstudio.md) describes
the narrower licensed adapter. Optiland snippets do not run unchanged through ZOSPy.

## Audited refocus demo

The original deterministic refocus example remains available:

```sh
npx optical-design demo --out audited-focus
```

It searches only the synthetic singlet's final air gap and writes machine-readable
evidence and a review into a new directory. Read the acceptance checks and
saved-candidate verification. Rendering alone does not establish optical success.

[Capabilities](capabilities.md) · [Installation and recovery](install.md) ·
[Compatibility](compatibility.md)
