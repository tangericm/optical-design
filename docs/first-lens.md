# Start with an example

[Documentation](README.md) / Example workflow

Run the bundled lens workflow to check your setup and see what the tool produces.
It uses a synthetic singlet and needs no OpticStudio license.

## Run it

Install [Node.js](https://nodejs.org/en/download) 22+ and
[uv](https://docs.astral.sh/uv/getting-started/installation/), then open a terminal in
your project folder:

```sh
npx optical-design doctor
npx optical-design demo --out my-first-lens
```

Use a new output directory. The first run may download Python and Optiland.

The demo calculates a diffraction limit, adjusts the example lens's final air gap,
verifies the saved candidate, and creates an HTML review. Open the review path printed
at completion. The source model stays unchanged.

Prefer individual commands? Use the [manual quickstart](quickstart.md).

## Read the result

| Output | What to look for |
|---|---|
| Job outcome | Whether the candidate improved and met the stated requirements |
| Prescription changes | The original and final spacing, with the remaining lens geometry fixed |
| Analysis settings | Fields, wavelengths, sampling, metric definitions, and units |
| Saved-model checks | Whether the saved and reloaded candidate matches the reported result |
| Review package | A readable view of the recorded evidence; it can also describe a failed job |

The example demonstrates a supported workflow. Its requirements are specific to the
synthetic model. An HTML report is not, by itself, proof that an optical design passed.
Use the [glossary](glossary.md) for unfamiliar terms.

## Use your own model

[Install the skill into your agent](install.md), then give it a saved prescription and
the outcome you want. For example:

> Use optical-design to inspect [model path]. Check that its surface types and analysis
> assumptions are supported. Summarize the current design, identify the inputs needed
> to assess [my requirement], and preserve the source model.

If you already have a specification, continue with the
[professional workflow](professional-workflow.md). For supported models and available
operations, see [capabilities and limits](capabilities.md).
