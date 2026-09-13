# optical-design

**Give your AI assistant an optical-design workflow you can inspect.**

Calculate optical performance, work on saved sequential lens models, and turn results
into a review package. Includes numerical tools, a portable Optiland backend, and a
licensed OpticStudio backend.

[Get started](docs/quickstart.md) · [Documentation](docs/README.md) · [Releases](https://github.com/tangericm/optical-design/releases) · [Report an issue](https://github.com/tangericm/optical-design/issues)

## Install

For **Claude Code, Codex, Cursor, and other supported agents**, run this in a terminal
and choose your agent and installation scope:

```sh
npx skills add tangericm/optical-design
```

Prefer **Claude Code's plugin manager**? Run these inside Claude Code:

```text
/plugin marketplace add tangericm/optical-design
/plugin install optical-design@optical-design
```

This installs the skill: instructions, scripts, examples, and references your assistant
can use. Running the scripts needs **Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)**.
Start with the portable example; **OpticStudio is optional**.

[Installation by client, updates, and troubleshooting →](docs/install.md)

## Try it

Start a new conversation in your agent and ask:

> Use optical-design to calculate the Airy first-zero radius and diameter at 550 nm
> and f/4. Run the calculator, show the units, and explain the assumptions.

Then try a complete workflow on the included synthetic lens:

> Use optical-design's bundled portable singlet and refocus specification. Run a
> bounded refocus, check the saved candidate and requirements, and create an HTML
> review. Preserve the source model and put the outputs in a new folder.

Want to run the commands yourself? [Follow the quickstart](docs/quickstart.md).
It takes you from a calculator result to a saved lens and readable report.

## From a model to a decision

**Inspect → Set requirements → Edit or optimize → Validate → Review**

Every design job works on a copy. Reports record settings, engine versions, file hashes,
requirements, and saved-model checks so you can see what changed and why it passed or failed.

| Your task | Start here |
|---|---|
| Calculate resolution, Gaussian beams, PSF/MTF, or aberrations | [Numerical tools and compute tiers](docs/tiers.md) |
| Inspect a prescription or make an explicit edit | [Model inspection and edits](skills/optical-design/references/model-actions.md) |
| Refocus or optimize a saved lens | [Design workflow](skills/optical-design/references/design-workflow.md) and [optimization](skills/optical-design/references/optimization.md) |
| Evaluate sensitivity, tolerances, or extra fields and wavelengths | [Sensitivity](skills/optical-design/references/sensitivity.md), [tolerancing](skills/optical-design/references/tolerancing.md), and [validation](skills/optical-design/references/validation.md) |
| Share results or control jobs interactively | [Review packages](skills/optical-design/references/review-reports.md) and [optional MCP setup](skills/optical-design/references/interactive.md) |

## Current boundaries

The design workflow supports a **bounded subset of centered sequential imaging systems**.
The portable backend handles spherical/plane prescriptions; the native backend also
supports fixed Standard conics and EvenAspheric coefficients. Optimization changes up
to four declared radius/thickness variables. Analyses are scalar.

New-lens synthesis, glass selection during optimization, non-sequential/stray-light
design, and live OpticStudio GUI attachment are outside the shipped scope. A passing
numerical report is evidence for its stated conditions, not manufacturing certification.

[Full capabilities and model limits](docs/capabilities.md) · [Compatibility and verification evidence](docs/compatibility.md)

## How it is distributed

**v1.0.0 is released on GitHub.** The command above runs the npm-hosted `skills`
installer, which downloads this repository. An `optical-design` npm package and
`npx optical-design` command have not been published. Native marketplace listings
are separate from a GitHub release or npm publication.

[Understand skills, plugins, npm, and marketplaces →](docs/deployment.md)

## Contribute or get help

[Report a bug or request a feature](https://github.com/tangericm/optical-design/issues).
Include your agent, operating system, command, engine version, and error. Use a
synthetic example when reporting a problem with a private prescription.

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## License

[MIT](LICENSE).
