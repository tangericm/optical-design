# optical-design

An optical-design copilot for the saved sequential-imaging prescription workflow:
inspect a model, define requirements and composite merit, make controlled edits, optimize,
measure sensitivity, validate separately, and produce a design-review package.
Includes a portable Optiland adapter and OpticStudio standalone adapters.

The job workflow copies a model, measures a baseline, searches explicit parameter bounds,
checks every hard requirement, and verifies the saved/reloaded candidate. It records engine
versions, settings, search history and file hashes. The source model stays unchanged.

| Capability | Shipped scope |
|---|---|
| Numerical optics | Resolution, Gaussian beams, Zernike/Seidel math, pupil PSF/MTF, interferometry |
| Inspection and edits | Physical prescription inspection; explicit radius/thickness edits with expected-value checks, fixed-state verification and saved reload |
| Prescription audit | Explicit fields, wavelengths, metric identities, units and hard requirements |
| Refocus | Final air gap only; bounded search; fixed prescription invariants; native save/reload verification |
| Optimization | Up to four explicit radius/thickness variables; bounded search, hard requirements and saved-candidate verification |
| Composite merit | Dimensionless weighted RMS across explicit metrics, fields and wavelengths; target, scale, weight and residual evidence for each term |
| Local sensitivity | Central differences at declared radius/thickness steps; derivatives, finite-step effects and nonlinearity; rankings within a metric and unit |
| Separate validation | Predeclared requirements at extra fields/wavelengths or finer sampling; saved winner checked after search; failure rejects candidate |
| Tolerance evidence | Seeded independent radius/thickness perturbations, optional bounded focus compensation, paired pass rates and Wilson intervals |
| Review package | Standalone HTML and Markdown; verified artifact hashes, metric comparisons, parameter changes, sampled charts and an axial vertex schematic |
| Interactive MCP tools | Local stdio capabilities/start/status/cancel/results/review; owned jobs and confined input/output paths |
| Catalog shortlist | Local declared records, identity/provenance validation, unit-aware constraints and ranking |
| Native profile benchmark | Copied-model Huygens/POP central intensity cuts, explicit settings and hashes, native sampling diagnostics, optional same-method reference comparison |
| Guidance | Specifications, microscopy, OCT, interferometry, optimization, PSF/MTF and tolerancing references |

Start with [the executable workflow and specification](skills/optical-design/references/design-workflow.md).
Synthetic native/portable singlets and example specifications are included under
`skills/optical-design/assets/`.

For validation beyond the search settings, see [separate validation](skills/optical-design/references/validation.md).
For complete field/spectral requirements, run the [three-field, three-wavelength example](skills/optical-design/references/field-validation-example.md).
For interactive jobs, see [the MCP interface](skills/optical-design/references/interactive.md).
For bounded multivariable jobs, see [optimization](skills/optical-design/references/optimization.md).
For a complete runnable example, see [workflow scenarios](skills/optical-design/evals/README.md).

For unchanged-model profile reproduction, use the [profile benchmark workflow](skills/optical-design/references/profile-benchmark.md).
The [real-design reference audit](docs/research/real-benchmark/reference-audit.md) documents
the saved OCT evidence, exact model hashes, spectrum, units and uncertainty. Its 75 saved
model/case records are reference inputs; their existence does not establish a successful
fresh native run or physical design acceptance. The completed run and later controlled
experiments are documented in [the dev.3 evidence](docs/research/next-roadmap/README.md).

## Install

Install from the GitHub repository:

- Agent Skills: `npx skills add tangericm/optical-design`
- Claude Code: `claude plugin marketplace add tangericm/optical-design`, then `claude plugin install optical-design@optical-design`

`npx skills add` uses the GitHub skill. The `optical-design` npm package is not published;
`npx optical-design` is not this project's installation command.

Scripts need Python 3.11+ and uv. Tier 0 dependencies are declared in scripts.
Prescription commands use pinned optional engines; see [tiers](docs/tiers.md) and
[compatibility evidence](docs/compatibility.md).

## Current boundaries

The native prescription adapter supports centered Standard conic and EvenAspheric
sequential refractive systems in mm with angle fields and entrance-pupil diameter.
Conics and all eight even-asphere coefficients remain fixed during edits and optimization.
The portable adapter supports its documented spherical/plane contract. Analyses are scalar.
Coatings, coordinate breaks, multiple configurations and unsupported surface types reject.
The separate native profile backend analyzes mm,
single-configuration sequential models with complex surfaces and explicit native polarization
settings. POP currently supports a declared Gaussian-waist launch; this is not generalized
validation of arbitrary models, source fields or polarization assumptions.

Topology changes, glass selection during optimization, live GUI attachment, arbitrary portable Zemax imports,
non-sequential/stray-light analysis and manufacturing release are not shipped. The restricted
portable ZMX importer rejects unsupported directives instead of silently dropping them.
Tolerance pass rates depend on the declared perturbation model. Profile reference agreement
means same-method numerical reproduction; illumination cuts are not point-image PSFs,
integrated marginals or measured OCT performance.

See [CHANGELOG](CHANGELOG.md) for changes and [SECURITY](SECURITY.md) for execution behavior.

## License

MIT.
